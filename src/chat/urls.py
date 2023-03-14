# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name="login"),
    path("register/", views.register_view, name="index"),
    path("index/", views.room_option, name="index"),
    path("chat/<str:room_name>/", views.chatroom, name="room"),
    path('logout/', views.logout_view, name = "logout" ),
]