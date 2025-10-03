from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_ai, name="test_ai"),
]
