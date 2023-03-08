from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.hashers import make_password, check_password
from chat.models import User, Room, Message
from django.contrib.auth import authenticate, login, logout, get_user_model

user =  get_user_model()

def register_view(request):
    if request.method == 'POST':
      
      username = request.POST['username']
      email = request.POST['email']
      password = request.POST['password']
      pass_confirm = request.POST['password_confirm']

      if password == pass_confirm:
          hashed_password = make_password(password)
          user = User.objects.create(username = username, email = email, password = hashed_password)
          user.save()
          
          return HttpResponseRedirect(reverse('login'))
      else:
           context = { 'error' : "Mật khẩu bạn nhập chưa chính xác"}
           return render(request, 'chat/register.html', context)
    return render(request, 'chat/register.html')

def login_view(request):
    if request.method == 'POST':
        username =  request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'chat/login.html', context)
        
    return render(request, 'chat/login.html')

def room_list(request):
    rooms = Room.objects.all()
    return render( request, 'chat/index.html', {'rooms': rooms})



@login_required
def chatroom(request, room_name):

    if request.user.is_authenticated:
        username = request.user.username

    return render( request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'username':mark_safe(json.dumps(username)),
        })


def logout_view(request):
    print("da logout thanh cong")
    logout(request)
    return HttpResponseRedirect(reverse('login'))