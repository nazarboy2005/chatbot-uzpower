from django.urls import path
from ai.views import ChatView

app_name = 'ai'

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
]
