from django.contrib.auth import get_user_model, authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer,UserProfileSerializer,OrderSerializer
from django.conf import settings
from django.middleware import csrf
from django.http import JsonResponse
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status
from django.utils import timezone
from .models import UserAccount,Order
import environ
import razorpay
import json
from django.conf import settings
from django.shortcuts import get_object_or_404



User = get_user_model()


class SignupView(APIView):


    def post(self, request, format=None):
        data = self.request.data
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2')
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)  # Generate token
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            user.save()
            return Response(tokens, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
 
class LoginView(APIView):
    def post(self, request, format=None):
        data = request.data
        response = Response()
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(email=email, password=password)
        if user is not None:
            if not user.is_active:
                return Response({"No active": "This account is not active!!"}, status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
            data = get_tokens_for_user(user)
            response = JsonResponse({
                "data": data,
                "user": {
                    "id": user.id,
                    "username": user.email,
                    "name": user.name,
                }
            })
            
            response.set_cookie(
                key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                value = data["access"],
                expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            csrf.get_token(request)
            response.data = {"Success" : "Login successfully","data":data}
            return response
        else:
            return Response({"Invalid" : "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)



class LogoutView(APIView):
    def get(self, request):
        response = JsonResponse({"message": "Logged out successfully"})

        # Clear the authentication cookie
        response.delete_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            path='/',
            domain=settings.SIMPLE_JWT.get('AUTH_COOKIE_DOMAIN', None)  # Set to None if not present
        )

        # Expire the cookie immediately
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value='',
            expires=timezone.now() - timedelta(days=1),
            path='/',
            domain=settings.SIMPLE_JWT.get('AUTH_COOKIE_DOMAIN', None)  # Set to None if not present
        )
        

        return response
    
  
    
class UserProfileView(APIView):

    def get(self, request):
        user_profile = request.user
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def put(self, request):
        user_profile = request.user
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_profile = request.user
        user_profile.delete()
        return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class start_paymentView(APIView):
    def post(self, request, *args, **kwargs):
        # request.data is coming from frontend
        amount = request.data.get('amount')
        name = request.data.get('name')
        if not amount or not name:
            return Response({"error": "Amount and Name are required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # setup razorpay client this is the client to whom the user is paying money
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # create razorpay order
        # the amount will come in 'paise' that means if we pass 50, the amount will become
        # 0.5 rupees, so we have to convert it to rupees. We will multiply it by 100.
        payment = client.order.create({"amount": int(amount) * 100, 
                                       "currency": "INR", 
                                       "payment_capture": "1"})

        # We are saving an order with isPaid=False because we've just initialized the order
        # We haven't received the money; we will handle the payment success in the next function
        order = Order.objects.create(order_person=name, 
                                     order_amount=amount, 
                                     order_payment_id=payment['id'])

        serializer = OrderSerializer(order)
        
        """order response will be 
            {'id': 17, 
            'order_date': '23 January 2021 03:28 PM', 
            'order_product': '**product name from frontend**', 
            'order_amount': '**product amount from frontend**', 
            'order_payment_id': 'order_G3NhfSWWh5UfjQ', # it will be unique everytime
            'isPaid': False}"""

        data = {
            "payment": payment,
            "order": serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED)


class handle_payment_successView(APIView):
    def post(self, request, *args, **kwargs):
        res = json.loads(request.data["response"])
        """res will be:
        {'razorpay_payment_id': 'pay_G3NivgSZLx7I9e', 
        'razorpay_order_id': 'order_G3NhfSWWh5UfjQ', 
        'razorpay_signature': '76b2accbefde6cd2392b5fbf098ebcbd4cb4ef8b78d62aa5cce553b2014993c0'}
        this will come from frontend which we will use to validate and confirm the payment
        """

        ord_id = ""
        raz_pay_id = ""
        raz_signature = ""

        # res.keys() will give us list of keys in res
        for key in res.keys():
            if key == 'razorpay_order_id':
                ord_id = res[key]
            elif key == 'razorpay_payment_id':
                raz_pay_id = res[key]
            elif key == 'razorpay_signature':
                raz_signature = res[key]

        # get order by payment_id which we've created earlier with isPaid=False
        order = Order.objects.get(order_payment_id=ord_id)

        # we will pass this whole data in razorpay client to verify the payment
        data = {
            'razorpay_order_id': ord_id,
            'razorpay_payment_id': raz_pay_id,
            'razorpay_signature': raz_signature
        }

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # checking if the transaction is valid or not by passing above data dictionary in 
        # razorpay client if it is "valid" then check will return None
        check = client.utility.verify_payment_signature(data)

        if check is not None:
            order.isPaid = True
            order.save()
            return Response({'error': 'Something went wrong'})

        # if payment is successful that means check is None then we will turn isPaid=True
        # order.isPaid = True
        # order.save()

        res_data = {
            'message': 'payment successfully received!'
        }

        return Response(res_data)

