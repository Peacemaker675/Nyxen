import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.target_username = self.scope['url_route']['kwargs']['username']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.conversation = await self.get_or_create_conversation()

        if not self.conversation:
            await self.close()
            return

        self.room_group_name = f"chat_{self.conversation.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        saved_message = await self.save_message(message_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': self.user.username,
                'timestamp': saved_message.timestamp.strftime("%H:%M:%S")
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_or_create_conversation(self):
        try:
            target_user = User.objects.get(username=self.target_username)
            if target_user not in self.user.friends.all():
                return None

            conversation = Conversation.objects.filter(
                (Q(user1=self.user) & Q(user2=target_user)) |
                (Q(user1=target_user) & Q(user2=self.user))
            ).first()

            if not conversation:
                conversation = Conversation.objects.create(user1=self.user, user2=target_user)
            
            return conversation
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content):
        return Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content=content
        )