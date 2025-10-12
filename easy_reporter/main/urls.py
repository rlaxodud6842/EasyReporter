from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('upload_image/', views.upload_image,name="upload_image"),
    path('submit_report/',views.submit_report,name="submit_report"),
    path("api/chat/", views.chat_api,name="submit_report"),
]
