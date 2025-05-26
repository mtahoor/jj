from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("test-messages/", views.test_messages, name="test_messages"),
    path("test-toast/", views.test_toast, name="test_toast"),
]
