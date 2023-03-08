# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import User, Room, Message
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from django.db.models import QuerySet

class ChatConsumer(AsyncWebsocketConsumer):
        
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

      
        await self.accept()
        messages = await database_sync_to_async (self.get_history_message)()

        messages_json_arr = []
        for message in messages:
            messages_json_arr.append({
                'id': message.id,
                'username': (message.user).username,
                'content': message.content
            })
        print(messages_json_arr)
        await self.send(text_data=json.dumps({
            'arrMessages': messages_json_arr
        }))


    def get_history_message(self):
        room1 = Room.objects.get(name=self.room_name)
        queryset  = Message.objects.filter(room = room1.id)
        array_of_objects = list(queryset)
        print(array_of_objects)
        return array_of_objects
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    
    # Receive message from WebSocket
    async def receive(self, text_data):
        print(text_data)
        data = json.loads(text_data)
        command = data['command']
        message = data['message']
        from_user = data['from']
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'command': command,
                'message': message,
                'from':from_user
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
      
        command = event['command']
        message = event['message']
        from_user = event['from']
        await self.send(text_data=json.dumps({
            'command': command,
            'message': message,
            'from': from_user
        }))
        user = await database_sync_to_async(User.objects.get)(username=from_user)
        print(user)
        room = await database_sync_to_async(Room.objects.get)(name = self.room_name)
        content = event['message']
        message = await database_sync_to_async (Message.objects.create)(user = user, room = room, content = content)

     