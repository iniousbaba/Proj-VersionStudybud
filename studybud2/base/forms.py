from pyexpat import model
from attr import field
from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm


# from django.contrib.auth.models import User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = [
            "host",
            "participants",
        ]  # when you want to save some table items automatically and not on the form.


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "name", "avatar", "bio"]
