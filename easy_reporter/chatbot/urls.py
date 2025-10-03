from django.urls import path
from . import views

urlpatterns = [
    path('popup/', views.chat_popup, name="chat_popup"),
]
