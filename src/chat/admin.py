from django.contrib import admin

from .models import Message, User, Room

admin.site.register(Message)
admin.site.register(Room)
admin.site.register(User)
