
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
     groups = models.ManyToManyField(Group, related_name="chat_users")
     user_permissions = models.ManyToManyField(Permission, related_name="chat_users_permissions")
     pass


class Room(models.Model):
    name = models.CharField(max_length=255, unique= True)
    members = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=255,blank=True,null=True)
    def __str__(self):
        return self.name
    
    def last_10_messages(self):
         return Message.objects.filter(room_id=self.id).order_by('-timestamp').all()[:10]

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.user.username

    

