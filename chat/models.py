from django.db import models
from django.conf import settings

class Conversation(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_started', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This prevents duplicate conversations between the same two people
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Chat: {self.user1.username} & {self.user2.username}" #type: ignore

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M')}] {self.sender.username}: {self.content[:20]}" #type: ignore