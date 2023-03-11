# chat/consumers.py
from asyncio import sleep
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import User, Room, Message
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from django.db.models import QuerySet
import asyncio
import pytz
from datetime import datetime


def handletime(time):
    datetime_obj_utc = time.astimezone(pytz.utc)
    datetime_obj_vn = datetime_obj_utc.astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
    hour_minute_str = datetime_obj_vn.strftime('%H:%M')
    return hour_minute_str 

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

            timestamp = handletime(message.timestamp)

            messages_json_arr.append({
                'id': message.id,
                'username': (message.user).username,
                'content': message.content,
                'timestamp':timestamp
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
        
        data = json.loads(text_data)
        print(data)
        command = data['command']
        message = data['message']
        from_user = data['from']
        user_id = data['user_id']
        timestamp = data['timestamp']

        user = await database_sync_to_async(User.objects.get)(username=from_user)
        room = await database_sync_to_async(Room.objects.get)(name = self.room_name)
        content = message
        time = timestamp
        await database_sync_to_async (Message.objects.create)(user = user, room = room, content = content, timestamp = time)      

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'command': command,
                'message': message,
                'from':from_user,
                'user_id':user_id,
                'time': timestamp
                
            }
        )
    

    # Receive message from room group
    async def chat_message(self, event):
        
        command = event['command']
        message = event['message']
        from_user = event['from']
        timestamp = event['time']
       
        await self.send(text_data=json.dumps({
                        'command': command,
                        'message': message,
                        'from': from_user,
                        'time': timestamp
                    }))
            
     
            


     