from django.urls import path
from . import views

app_name = 'ai_integration'

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat'),
    path('search/', views.semantic_search, name='search'),
]