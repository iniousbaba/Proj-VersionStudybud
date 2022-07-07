from django.shortcuts import render, redirect

# import below for query db
from django.db.models import Q

# We are not using this in-built model. Instead we are cloning the model inn the forms.py page and then adding other features to suit our taste.
# # import below for in-bulit user
# from django.contrib.auth.models import User

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# import this below for error messages
from django.contrib import messages

# import this below for authentiaction
from django.contrib.auth import authenticate, login, logout

# import decorator below to restricit access to some fuctions
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# We are not using this in-built model. Instead we are cloning the model inn the forms.py page and then adding other features to suit our taste.
# import this for using in-built forms
# from django.contrib.auth.forms import UserCreationForm

# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets learn python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend developers'},

# ]


def loginPage(request):
    page = "login"

    # how to prevent users from re-login
    if request.user.is_authenticated:
        return redirect("home")

    #   The if method is to check if data has been filled
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        # check if user exisits
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist.")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Email or Password doesn't not exisit.")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


def user_logout(request):
    logout(request)
    return redirect("home")


def user_register(request):

    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(
                commit=False
            )  # This means python should hold the data for editing, before we finally save.
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")

    context = {"form": form}
    return render(request, "base/login_register.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    # the .filter method us to query the db using the search parameter thatwas loaded in the url link.
    # for items that has foreign key, you can also use __ to enter into the respective table and search for an item in the table.
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]  # [0:5] means reducing the data extracted TO 5
    # How to count the search result
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_message = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(  # This create function is to save data that's is not generated by the in-built form template
            user=request.user, room=room, body=request.POST.get("body")
        )

        room.participants.add(
            request.user
        )  # This is to add a user to the many-to-many relationship. You can alsouse .remove to remove a user
        return redirect(
            "room", pk=room.id
        )  # The essence of the redirect is to refresh the page after saving the data
    context = {"room": room, "room_message": room_message, "participants": participants}

    return render(request, "base/room.html", context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    rooms = user.room_set.all()

    context = {
        "user": user,
        "room_messages": room_messages,
        "topics": topics,
        "rooms": rooms,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        # How to get or create a topic instantly from a form
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )

        # form = RoomForm(request.POST)  # request.POST is all the data entered in a form.
        # if form.is_valid():
        #     room = form.save(commit=False)  # Saving the form in the database
        #     room.host = request.user  # Automatically saving the host
        #     room.save()
        return redirect("home")  # Redirecting after save

    context = {"form": form, "topics": topics}  # Passing form to a webpage
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")

    form = RoomForm(
        instance=room
    )  # the instance means to specify the data to load to the form.

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.save()

        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect("home")

    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url="login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    # room = Room.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        message.delete()
        # return redirect("room", pk=room.id)
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})


@login_required(login_url="login")
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES,  instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    context = {"form": form}
    return render(request, "base/update-user.html", context)


def Topic_Page(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    topics = Topic.objects.filter(Q(name__icontains=q))
    context = {"topics": topics}
    return render(request, "base/topics.html", context)


def Activity_Page(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)
