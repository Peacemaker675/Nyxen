from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('history/<str:username>/', views.get_messages, name='get_messages'),
]