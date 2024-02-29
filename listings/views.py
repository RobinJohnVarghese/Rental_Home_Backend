from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView,UpdateAPIView,DestroyAPIView
from rest_framework import permissions
from rest_framework import status
from .models import Listing,Notifications,ChatRoom, Message
from .serializers import (ListingSerializer, listingDetailSerializer,
    CreatelistingSerializer,NotificationsSerializer,UserInterestsSerializer,
    MarkNotificationSerializer,MessageSerializer,ProfileSerializer,ChatRoomSerializer,
    ChatRoomListSerializer)
from accounts.models import UserAccount
from accounts.serializers import UserProfileSerializer
from datetime import datetime, timezone, timedelta
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from django.contrib.auth import get_user_model



class NoPagination(PageNumberPagination):
    page_size=None

class ListingsView(ListAPIView):
    queryset = Listing.objects.order_by('-list_date').filter(is_published=True)
    permission_classes = (permissions.AllowAny, )
    serializer_class = ListingSerializer
    lookup_field = 'slug'
    pagination_class = NoPagination
    
    

class ListingView(RetrieveAPIView):
    queryset = Listing.objects.order_by('-list_date').filter(is_published=True)
    serializer_class = listingDetailSerializer
    lookup_field = 'slug'
    
class UserListingView(ListAPIView):
    serializer_class = ListingSerializer
    pagination_class = NoPagination
    def get_queryset(self):
        realtor_id = self.kwargs.get('realtor_id')
        return Listing.objects.filter(realtor__id=realtor_id, is_published=True)
    
class SearchView(APIView):
    serializer_class = ListingSerializer

    def post(self, request, format=None):
        queryset = Listing.objects.order_by('-list_date').filter(is_published=True)
        data = self.request.data

        sale_type = data['sale_type']
        queryset = queryset.filter(sale_type__iexact=sale_type)

        price = data['price']
        if price == '$0+':
            price = 0
        elif price == '$200,000+':
            price = 200000
        elif price == '$400,000+':
            price = 400000
        elif price == '$600,000+':
            price = 600000
        elif price == '$800,000+':
            price = 800000
        elif price == '$1,000,000+':
            price = 1000000
        elif price == '$1,200,000+':
            price = 1200000
        elif price == '$1,500,000+':
            price = 1500000
        elif price == 'Any':
            price = -1
        
        if price != -1:
            queryset = queryset.filter(price__gte=price)
        
        bedrooms = data['bedrooms']
        if bedrooms == '0+':
            bedrooms = 0
        elif bedrooms == '1+':
            bedrooms = 1
        elif bedrooms == '2+':
            bedrooms = 2
        elif bedrooms == '3+':
            bedrooms = 3
        elif bedrooms == '4+':
            bedrooms = 4
        elif bedrooms == '5+':
            bedrooms = 5
        
        queryset = queryset.filter(bedrooms__gte=bedrooms)

        home_type = data['home_type']
        queryset = queryset.filter(home_type__iexact=home_type)

        bathrooms = data['bathrooms']
        if bathrooms == '0+':
            bathrooms = 0.0
        elif bathrooms == '1+':
            bathrooms = 1.0
        elif bathrooms == '2+':
            bathrooms = 2.0
        elif bathrooms == '3+':
            bathrooms = 3.0
        elif bathrooms == '4+':
            bathrooms = 4.0
        
        queryset = queryset.filter(bathrooms__gte=bathrooms)

        sqft = data['sqft']
        if sqft == '1000+':
            sqft = 1000
        elif sqft == '1200+':
            sqft = 1200
        elif sqft == '1500+':
            sqft = 1500
        elif sqft == '2000+':
            sqft = 2000
        elif sqft == 'Any':
            sqft = 0
        
        if sqft != 0:
            queryset = queryset.filter(sqft__gte=sqft)
        
        days_passed = data['days_listed']
        if days_passed == '1 or less':
            days_passed = 1
        elif days_passed == '2 or less':
            days_passed = 2
        elif days_passed == '5 or less':
            days_passed = 5
        elif days_passed == '10 or less':
            days_passed = 10
        elif days_passed == '20 or less':
            days_passed = 20
        elif days_passed == 'Any':
            days_passed = 0
        
        for query in queryset:
            num_days = (datetime.now(timezone.utc) - query.list_date).days

            if days_passed != 0:
                if num_days > days_passed:
                    slug=query.slug
                    queryset = queryset.exclude(slug__iexact=slug)
        
        has_photos = data['has_photos']
        if has_photos == '1+':
            has_photos = 1
        elif has_photos == '3+':
            has_photos = 3
        elif has_photos == '5+':
            has_photos = 5
        elif has_photos == '10+':
            has_photos = 10
        elif has_photos == '15+':
            has_photos = 15
        
        for query in queryset:
            count = 0
            if query.photo_1:
                count += 1
            if query.photo_2:
                count += 1
            if query.photo_3:
                count += 1
            if query.photo_4:
                count += 1
            if query.photo_5:
                count += 1
            if query.photo_6:
                count += 1
            if query.photo_7:
                count += 1
            if query.photo_8:
                count += 1
            if query.photo_9:
                count += 1
            if query.photo_10:
                count += 1
            if query.photo_11:
                count += 1
            if query.photo_12:
                count += 1
            if query.photo_13:
                count += 1
            if query.photo_14:
                count += 1
            if query.photo_15:
                count += 1
            if query.photo_16:
                count += 1
            if query.photo_17:
                count += 1
            if query.photo_18:
                count += 1
            if query.photo_19:
                count += 1
            if query.photo_20:
                count += 1
            
            if count < has_photos:
                slug = query.slug
                queryset = queryset.exclude(slug__iexact=slug)
        
        open_house = data['open_house']
        queryset = queryset.filter(open_house__iexact=open_house)

        keywords = data['keywords']
        queryset = queryset.filter(description__icontains=keywords)

        serializer = ListingSerializer(queryset, many=True)

        return Response(serializer.data)
    
  
class CreateListing(APIView):

    def post(self, request, *args, **kwargs):
        # Extract realtor from the request data
        realtor_id = request.data.get('realtor_id')
        # Ensure that the realtor is valid
        try:
            realtor = UserAccount.objects.get(id=realtor_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'realtor not found'}, status=status.HTTP_404_NOT_FOUND)

        # Associate the service with the realtor
        request.data['realtor'] = int(realtor.id)
        serializer = CreatelistingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ListingUpdateView(UpdateAPIView):
    queryset = Listing.objects.all()  # Assuming you want to update all listings
    serializer_class = listingDetailSerializer
    lookup_field = 'slug'
    
class ListingDeleteView(DestroyAPIView):
    queryset = Listing.objects.all()  
    serializer_class = listingDetailSerializer
    lookup_field = 'slug'




class ListingSearchView(APIView):
    serializer_class = ListingSerializer
        
    def get(self, request, *args, **kwargs):
        try:
            query = self.request.GET.get('query')
            if query is None:
                return Response({"error": "Query parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

            queryset = Listing.objects.filter(Q(title__icontains=query) | Q(address__icontains=query)
                                            | Q(city__icontains=query) | Q(state__icontains=query))

            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Send_interest(APIView):
    def post(self, request):
        fromuser_id = request.data.get('fromuser')
        touser_id = request.data.get('touser')  # Adjust this based on your request data
        intrested_post_id = request.data.get('postid')  # Adjust this based on your request data

        # Retrieve user instances and post instance
        fromuser = get_object_or_404(UserAccount, id=fromuser_id)
        touser = get_object_or_404(UserAccount, id=touser_id)
        intrested_post = get_object_or_404(Listing, id=intrested_post_id)

        # Check if the notification already exists
        existing_notification = Notifications.objects.filter(fromuser=fromuser, touser=touser, intrested_post=intrested_post).exists()

        if not existing_notification:
            # Create and save a new notification
            notification = Notifications(fromuser=fromuser, touser=touser, intrested_post=intrested_post)
            notification.save()

            # Serialize the notification and return the response
            serializer = NotificationsSerializer(notification)
            return Response({'message': 'Interest sent successfully', 'data': serializer.data}, status=200)
        else:
            return Response({'message': 'Interest already sent'}, status=400)





class AllUserInterestsView(ListAPIView):
    serializer_class = UserProfileSerializer
    pagination_class = NoPagination

    def get_queryset(self):
        # Retrieve the logged-in user
        logged_in_user = self.request.user
        # Fetch tousers when fromuser is the current user
        tousers = Notifications.objects.filter(fromuser=logged_in_user).values_list('touser', flat=True).distinct()
        # Get the UserAccount objects corresponding to the tousers
        tousers_users = UserAccount.objects.filter(pk__in=tousers)
        # Fetch fromusers when touser is the current user
        fromusers = Notifications.objects.filter(touser=logged_in_user).values_list('fromuser', flat=True).distinct()
        # Get the UserAccount objects corresponding to the fromusers
        fromusers_users = UserAccount.objects.filter(pk__in=fromusers)    
        combined_queryset = tousers_users.union(fromusers_users)
        return combined_queryset   


class UserInterestsView(ListAPIView):
    serializer_class = UserInterestsSerializer
    pagination_class = NoPagination

    def get_queryset(self):
        # Retrieve the logged-in user
        logged_in_user = self.request.user

        # Filter the queryset based on the logged-in user
        queryset = Notifications.objects.filter(touser=logged_in_user,is_seen=False)
        
        # If is_seen is False, filter out notifications with is_seen=True
    

        # Retrieve additional information for each notification
        for notification in queryset:
            # Retrieve fromuser's name and email
            fromuser_name = notification.fromuser.get_full_name()
            fromuser_email = notification.fromuser.email
            # Retrieve intrested_post's title and slug
            intrested_post_title = notification.intrested_post.title
            intrested_post_slug = notification.intrested_post.slug

            # Add additional fields to the notification instance
            notification.fromuser_name = fromuser_name
            notification.fromuser_email = fromuser_email
            notification.intrested_post_title = intrested_post_title
            notification.intrested_post_slug = intrested_post_slug
            
        return queryset


class MarkNotificationAsSeen(APIView):
    # authentication_classes = [TokenAuthentication]
    def post(self, request, pk,format=None):
        try:
            notification = Notifications.objects.get(pk=pk)
        except Notifications.DoesNotExist:
            return Response({"message": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        notification.is_seen = True
        notification.save()

        serializer = MarkNotificationSerializer(notification)
        return Response(serializer.data)
    

    
class SendMessages(generics.CreateAPIView):
    serializer_class = MessageSerializer
    
class ProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = UserAccount.objects.all()
    # permission_classes = [IsAuthenticated]
    

class CreateChatRoom(APIView):
    serializer_class = ChatRoomSerializer
 
    def post(self, request, cid,pk):
        cid = self.kwargs['cid']
        pk = self.kwargs['pk']
        current_user = UserAccount.objects.get(id=cid)
        other_user = UserAccount.objects.get(id=pk)

        # Check if a chat room already exists between the users
        existing_chat_rooms = ChatRoom.objects.filter(members=current_user).filter(members=other_user)
        if existing_chat_rooms.exists():
            serializer = ChatRoomSerializer(existing_chat_rooms.first())
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Create a new chat room
        chat_room = ChatRoom()
        chat_room.save()
        chat_room.members.add(current_user, other_user)
        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        userId = self.kwargs['userId']
        user = UserAccount.objects.get(id=userId)
        return ChatRoom.objects.filter(members=user)



class RoomMessagesView(APIView):
    serializer_class = MessageSerializer

    def get(self, request, roomId):  
        try:
            room = ChatRoom.objects.get(id=roomId)
            messages = Message.objects.filter(room=room)
            serialized_messages = self.serializer_class(messages, many=True).data
            return Response(serialized_messages, status=status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            return Response("Room not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


