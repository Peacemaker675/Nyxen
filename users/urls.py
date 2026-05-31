from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('request/send/', views.send_friend_request, name='send_friend_request'),
    path('request/accept/', views.accept_friend_request, name='accept_friend_request'),
    path('request/reject/', views.reject_friend_request, name='reject_friend_request'),
]