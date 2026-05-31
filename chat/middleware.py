from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_string):
    try:
        access_token = AccessToken(token_string)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except (TokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode('utf-8')
            if auth_header.startswith('Bearer '):
                token_string = auth_header.split(' ')[1]
                scope['user'] = await get_user_from_token(token_string)
            else:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()            
        return await super().__call__(scope, receive, send)