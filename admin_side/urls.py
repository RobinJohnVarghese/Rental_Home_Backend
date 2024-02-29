from django.urls import path
from .views import *


urlpatterns = [
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path('user-list/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/block/', UserBlockView.as_view(), name='user-block'),
    path('users/<int:user_id>/unblock/', UserUnblockView.as_view(), name='user-unblock'),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('users_Postmanagement/', PostManagementView.as_view(), name='user-list'),
    path('users_Postmanagement/<int:Listing_id>/block/', PostBlockView.as_view(), name='user-block'),
    path('users_Postmanagement/<int:Listing_id>/unblock/', PostUnblockView.as_view(), name='user-unblock'),
]  