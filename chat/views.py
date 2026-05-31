import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

@csrf_exempt
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)
        target_username = data.get('username')
        content = data.get('content')

        if not target_username or not content:
            return JsonResponse({"error": "Username and content are required"}, status=400)

        try:
            target_user = User.objects.get(username=target_username)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        if target_user not in request.user.friends.all():
            return JsonResponse({"error": "You can only message friends."}, status=403)

        # Find the conversation, or create it if this is the very first message
        conversation = Conversation.objects.filter( 
            (Q(user1=request.user) & Q(user2=target_user)) |
            (Q(user1=target_user) & Q(user2=request.user))
        ).first()

        if not conversation:
            conversation = Conversation.objects.create(user1=request.user, user2=target_user)

        # Create and save the message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        ) 

        return JsonResponse({
            "message": "Message sent!",
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@csrf_exempt
def get_messages(request, username):
    if request.method != 'GET':
        return JsonResponse({"error": "Only GET requests allowed"}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Find the conversation
    conversation = Conversation.objects.filter(
        (Q(user1=request.user) & Q(user2=target_user)) |
        (Q(user1=target_user) & Q(user2=request.user))
    ).first()

    if not conversation:
        return JsonResponse({"messages": []}) # No conversation yet, return empty list

    # Retrieve all messages, ordered by timestamp (oldest first)
    messages = conversation.messages.all()
    
    # Format the data into a clean JSON list
    message_data = []
    for msg in messages:
        message_data.append({
            "sender": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M:%S")
        })

    return JsonResponse({"messages": message_data}, status=200)