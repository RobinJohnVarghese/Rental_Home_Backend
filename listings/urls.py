from django.urls import path
from .views import (ListingsView, ListingView, SearchView,
    ListingSearchView,CreateListing,Send_interest,UserListingView,UserInterestsView,
    MarkNotificationAsSeen,ListingUpdateView,ListingDeleteView,AllUserInterestsView,
    SendMessages,ProfileDetail,CreateChatRoom,ChatRoomListView,RoomMessagesView)


urlpatterns = [
    path('', ListingsView.as_view()),
    path('my_listing/<int:realtor_id>/', UserListingView.as_view()),
    path('UserInterestsView', UserInterestsView.as_view()),
    path('AllUserInterestsView', AllUserInterestsView.as_view()),
    path('search', SearchView.as_view()),
    path('ListingSearchView', ListingSearchView.as_view()),
    path('<slug>', ListingView.as_view()),
    path('create_listing/', CreateListing.as_view(), name="createListing"),
    path('update/<slug>', ListingUpdateView.as_view()),
    path('delete/<slug>', ListingDeleteView.as_view()),
    path('send_interest/', Send_interest.as_view(), name="sendInterest"),
    path('mark-notification-as-seen/<int:pk>/', MarkNotificationAsSeen.as_view(), name='mark_notification_as_seen'),
    path("send-messages/", SendMessages.as_view()),
    path("profile/<int:pk>/", ProfileDetail.as_view()),
    path('chat-room-list/<int:userId>/', ChatRoomListView.as_view()),
    path('create-chat-room/<int:pk>/<int:cid>/', CreateChatRoom.as_view()),
    path('chat-room/<int:roomId>/', RoomMessagesView.as_view()),
    
]
