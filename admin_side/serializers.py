from rest_framework import serializers
from accounts.models import UserAccount
from listings.models import Listing



class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ( 'id','email', 'name', 'is_active', 'is_staff')
       
       
class AdminPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'