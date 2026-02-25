from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('c/<int:conversation_id>/', views.conversation_view, name='conversation'),
    path('api/conversations/new/', views.new_conversation, name='new_conversation'),
    path('api/conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('api/conversations/<int:conversation_id>/rename/', views.rename_conversation, name='rename_conversation'),
    path('api/conversations/<int:conversation_id>/messages/', views.get_messages, name='get_messages'),
    path('api/send/', views.send_message, name='send_message'),
]
