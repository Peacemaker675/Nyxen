from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.api_login, name='login'),
    path('logout/', views.api_logout, name='logout'),
    path('request/send/', views.send_friend_request, name='send_friend_request'),
    path('request/accept/', views.accept_friend_request, name='accept_friend_request'),
    path('request/reject/', views.reject_friend_request, name='reject_friend_request'),
]