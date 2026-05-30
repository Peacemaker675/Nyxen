import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate, login, logout

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
            
            return JsonResponse({
                "message": "User created successfully!", 
                "username": user.username
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
            
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    "message": "Login successful!", 
                    "username": user.username
                })
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
            
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@csrf_exempt
def api_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({"message": "Successfully logged out!"})
        
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)