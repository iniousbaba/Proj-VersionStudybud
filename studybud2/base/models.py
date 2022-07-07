from email.policy import default
from django.db import models

# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    # you need to install pillow using pip for image to work
    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


# Create your models here.

# NB: always return the value you want to access later in the code


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(
        null=True, blank=True
    )  # null and blank is true here, means you can leave if blank and enter data another time.
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    updated = models.DateTimeField(
        auto_now=True
    )  # auto_now = Everytime the room info is update, record the date & time the change occured.
    created = models.DateTimeField(
        auto_now_add=True
    )  # auto_now_add = Record the date & time the room was created. This happens omly once

    class Meta:
        ordering = [
            "-updated",
            "-created",
        ]  # This determines how the data is dipslayed from the db like in SQL

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # models.CASCADE = delete all the children if the parent id is deleted. while models.null = Leave the data without a parent id controlling it.
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE
    )  # models.ForeignKey = it's for one to many relationships
    body = models.TextField()  # null is false here, means you must enter data
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated", "-created"]

    def __str__(self):
        return self.body[0:50]  # [0:50] = Get the first 50 charxters of the body text
