import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from accounts.models import UserAccount
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from .models import Message, ChatRoom
from .serializers import MessageSerializer,UserSerializer
from django.utils.timesince import timesince
from django.contrib.auth import get_user_model



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.realtor_id = self.scope['url_route']['kwargs']['realtor_id']
        realtor = await self.get_realtor_instance()

        if realtor:
            self.room_group_name = f"notify_{realtor.id}" 
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            await self.send(text_data=json.dumps({
                'message': 'connected',
            }))

        else:
            await self.close()

    async def get_realtor_instance(self):
        try:
            return await database_sync_to_async(UserAccount.objects.get)(id=self.realtor_id)
        except UserAccount.DoesNotExist:
            return None
    
            

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({'status': 'OK'}))

    async def send_notification(self, event):
        data = json.loads(event.get('value'))
        await self.send(text_data=json.dumps({
                'type' : 'notification',
                'payload': data,
                'notification_count': len(data),
            }))
        
    async def logout_user(self, event):
        await self.send(text_data=json.dumps({
            'type': 'logout'
        }))
        

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"
        # Add the channel to the room's group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Accept the WebSocket connection
        await self.accept()
        # Send a connection message to the client

    async def disconnect(self, close_code):
        # Remove the channel from the room's group upon disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )




    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_email = text_data_json['sender']

        new_message = await self.create_message(self.room_id, message, sender_email)
        
        # Send the received message to the room's group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'room_id': self.room_id,
                'sender_email': sender_email,
                'created': timesince(new_message.timestamp),
            }
        )



    async def chat_message(self, event):
        message = event['message']
        room_id = event['room_id']
        email = event['sender_email']
        created = event['created']

        # Send the chat message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'content': message,
            'room': room_id,
            'sender_email': email,
            'created': created,
        }))

    @sync_to_async
    def create_message(self, room_id, message, email):
        user = UserAccount.objects.get(email=email)
        room = ChatRoom.objects.get(id=room_id) 
        message = Message.objects.create(content=message, room=room, sender=user)
        message.save()
        return message

        
        




        
        