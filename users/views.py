import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate, login, logout
from .models import FriendRequest
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({"error": "Username and password are required"}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)
            
            user = User.objects.create_user(username=username, password=password)
            refresh = RefreshToken.for_user(user)
            
            return JsonResponse({
                "message": "User created successfully!", 
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh)             
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
            
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    
@csrf_exempt
def send_friend_request(request):

	if request.method != 'POST':
		return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
	if not request.user.is_authenticated:
		return JsonResponse({"error": "You must be logged in to send a friend request."}, status=401)

	try:
		data = json.loads(request.body)
		target_username = data.get('username')

		if not target_username:
			return JsonResponse({"error": "Please provide a username to add."}, status=400)

		if target_username == request.user.username:
			return JsonResponse({"error": "You cannot add yourself as a friend."}, status=400)

		try:
			target_user = User.objects.get(username=target_username)
		except User.DoesNotExist:
			return JsonResponse({"error": "User not found."}, status=404)

		if target_user in request.user.friends.all():
			return JsonResponse({"error": f"You are already friends with {target_username}."}, status=400)

		if FriendRequest.objects.filter(from_user=request.user, to_user=target_user).exists(): #type: ignore
			return JsonResponse({"error": "You already sent a request to this user."}, status=400)

		if FriendRequest.objects.filter(from_user=target_user, to_user=request.user).exists(): #type: ignore
			return JsonResponse({"error": f"{target_username} already sent you a request! Check your pending requests."}, status=400)

		FriendRequest.objects.create(from_user=request.user, to_user=target_user) #type: ignore

		return JsonResponse({"message": f"Friend request successfully sent to {target_username}!"}, status=201)
	except json.JSONDecodeError:
		return JsonResponse({"error": "Invalid JSON payload"}, status=400)


@csrf_exempt
def accept_friend_request(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
        
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to accept a friend request."}, status=401)

    try:
        data = json.loads(request.body)
        sender_username = data.get('username')

        if not sender_username:
            return JsonResponse({"error": "Please provide the username of the person you want to accept."}, status=400)

        try:
            sender = User.objects.get(username=sender_username)
            friend_request = FriendRequest.objects.get(from_user=sender, to_user=request.user) #type: ignore
            request.user.friends.add(sender)

            friend_request.delete()

            return JsonResponse({"message": f"You are now friends with {sender_username}!"}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
        except FriendRequest.DoesNotExist: #type: ignore
            return JsonResponse({"error": "No pending friend request from this user."}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)


@csrf_exempt
def reject_friend_request(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
        
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in."}, status=401)

    try:
        data = json.loads(request.body)
        sender_username = data.get('username')

        try:
            sender = User.objects.get(username=sender_username)
            friend_request = FriendRequest.objects.get(from_user=sender, to_user=request.user) #type: ignore
            friend_request.delete()
            return JsonResponse({"message": f"Friend request from {sender_username} rejected."}, status=200)

        except (User.DoesNotExist, FriendRequest.DoesNotExist): #type: ignore
            return JsonResponse({"error": "No pending friend request from this user."}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)