from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from .serializers import AdminSerializer,AdminPostSerializer
from rest_framework import generics, permissions, status
from accounts.models import *
from listings.models import Listing
from accounts.serializers import UserRegistrationSerializer
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from listings.serializers import ListingSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
# Create your views here.




class AdminLoginView(APIView):
    permission_classes = (permissions.AllowAny, )
    
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        print("user name : ", email, "password : ", password)
        user = authenticate(request, email=email, password=password)
        print("authenticate : ", user)
        if user is not None and user.is_staff:
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.name,
                    'email': user.email,
                    # Add other user details as needed
                }
            }
            return Response(tokens, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
class UserListView(APIView):
    def get(self, request, format=None):
        users = UserAccount.objects.all()
        serializer = AdminSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserBlockView(APIView):
    def post(self, request,user_id, format=None):
        user = UserAccount.objects.get(id=user_id)
        user.is_active = False
        user.save()
        serializer = AdminSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class UserUnblockView(APIView):
    def post(self, request, user_id, format=None):
        user = UserAccount.objects.get(id=user_id)
        user.is_active = True
        user.save()
        serializer = AdminSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSearchView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            search_term = request.query_params.get('search', '')
            users = UserAccount.objects.filter(
                Q(name__icontains=search_term) |
                Q(email__icontains=search_term)

            )
            serializer = UserRegistrationSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class NoPagination(PageNumberPagination):
    page_size=None

class PostManagementView(ListAPIView):
    queryset = Listing.objects.all().order_by('-list_date')
    permission_classes = (permissions.AllowAny, )
    serializer_class = AdminPostSerializer
    lookup_field = 'slug'
    pagination_class = NoPagination

    
class PostBlockView(APIView):
    def post(self, request, Listing_id, format=None):
        try:
            listing = Listing.objects.get(id=Listing_id)
        except Listing.DoesNotExist:
            return Response({"detail": "Listing not found."}, status=status.HTTP_404_NOT_FOUND)

        if listing.is_published:
            listing.is_published = False
            listing.save()
            serializer = AdminPostSerializer(listing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Listing is already blocked."}, status=status.HTTP_400_BAD_REQUEST)
    


class PostUnblockView(APIView):
    def post(self, request, Listing_id, format=None):
        try:
            listing = Listing.objects.get(id=Listing_id)
        except Listing.DoesNotExist:
            return Response({"detail": "Listing not found."}, status=status.HTTP_404_NOT_FOUND)

        if not listing.is_published:
            listing.is_published = True
            listing.save()
            serializer = AdminPostSerializer(listing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Listing is already unblocked."}, status=status.HTTP_400_BAD_REQUEST)
