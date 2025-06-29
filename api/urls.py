from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('family/overview/', views.family_overview, name='family_overview'),
    path('ai/chat/', views.ai_chat, name='ai_chat'),
]