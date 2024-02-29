from rest_framework import serializers
from .models import Listing,Notifications,ChatRoom, Message
from accounts.models import UserAccount
from accounts.serializers import UserProfileSerializer
from django.utils.timesince import timesince



class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ('id','title', 'address', 'city', 'state', 'price', 'sale_type', 'home_type', 'bedrooms', 'bathrooms', 'sqft', 'photo_main', 'slug')

class listingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        lookup_field = 'slug'
        


class CreatelistingSerializer(serializers.ModelSerializer):
    realtor_id = serializers.IntegerField(write_only=True, required=False)
    realtor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Listing
        fields = ['realtor_id', 'realtor', 'slug', 'title', 'address', 'city', 'state', 'zipcode',
                  'description', 'sale_type', 'price', 'bedrooms', 'bathrooms', 'home_type',
                  'sqft', 'open_house', 'photo_main', 'photo_1', 'photo_2', 'photo_3',
                  'photo_4', 'photo_5']
        read_only_fields = ['realtor']

    def create(self, validated_data):
        realtor_id = validated_data.pop('realtor_id', None)
        
        if realtor_id is not None:
            try:
                realtor = UserAccount.objects.get(id=realtor_id)
                validated_data['realtor'] = realtor
            except UserAccount.DoesNotExist:
                raise serializers.ValidationError({'realtor_id': 'Realtor with the provided ID does not exist.'})

        return super().create(validated_data)

class NotificationsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notifications
        fields = ['fromuser', 'touser', 'intrested_post', 'send_time', 'is_seen']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['fromuser'] = instance.fromuser.id  # Replace 'username' with the actual field you want to display
        representation['touser'] = instance.touser.id  # Replace 'username' with the actual field you want to display
        representation['intrested_post'] = instance.intrested_post.id  # Replace 'title' with the actual field you want to display
        return representation
    
    
class UserInterestsSerializer(serializers.ModelSerializer):
    fromuser_name = serializers.CharField(source='fromuser.get_full_name', read_only=True)
    fromuser_email = serializers.EmailField(source='fromuser.email', read_only=True)
    intrested_post_title = serializers.CharField(source='intrested_post.title', read_only=True)
    intrested_post_slug = serializers.CharField(source='intrested_post.slug', read_only=True)

    class Meta:
        model = Notifications
        fields = ['id','fromuser_name', 'fromuser_email', 'intrested_post_title', 'intrested_post_slug', 'send_time', 'is_seen']
        
        
class MarkNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAccount
        fields = ['id', 'name', 'email', 'phone', 'age', 'photo', 'description']

    
    def __init__(self, *args, **kwargs):
        super(ProfileSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method=='POST':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3       
 
    

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    created = serializers.SerializerMethodField(read_only=True)
    sender_first_name = serializers.SerializerMethodField(read_only=True)
    sender_profile_image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Message
        fields = ['room', 'sender_profile_image','sender', 'content', 'timestamp', 'is_seen', 'sender_email', 'created', 'sender_first_name']
    
    def get_created(self, obj):
        return timesince(obj.timestamp)
    
    def get_sender_first_name(self, obj):
        return obj.sender.name if obj.sender else None
    
    def get_sender_profile_image(self, obj):
        return obj.sender.photo.url if obj.sender and obj.sender.photo else None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id','email', 'name', 'phone', 'age', 'photo', 'description']


class ChatRoomListSerializer(serializers.ModelSerializer):
    unseen_message_count = serializers.SerializerMethodField()
    members = UserSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = '__all__'

    def get_unseen_message_count(self, obj):
        user = self.context['request'].user
        return Message.objects.filter(room=obj, is_seen=False).exclude(sender=user).count()

    def to_representation(self, instance):
        user = self.context['request'].user
        members = instance.members.exclude(id=user.id)
        data = super(ChatRoomListSerializer, self).to_representation(instance)
        data['members'] = UserSerializer(members, many=True).data
        return data