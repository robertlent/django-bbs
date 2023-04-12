from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Room, Topic, Message
from .forms import RoomForm


def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')

    context = {'page': page}

    return render(request, 'main/login_register.html', context)


def logout_user(request):
    logout(request)

    return redirect('home')


def register_user(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)

            return redirect('home')
        else:
            messages.error(request, 'An error occurring during registration.')

    return render(request, 'main/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q))
    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}

    return render(request, 'main/home.html', context)


def room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    room_messages = room.message_set.all().order_by('-created')

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        return redirect('room', primary_key=room.id)

    context = {'room': room, 'room_messages': room_messages}

    return render(request, 'main/room.html', context)


@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('home')

    context = {'form': form}

    return render(request, 'main/room_form.html', context)


@login_required(login_url='/login')
def update_room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not authorized to do that!")

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)

        if form.is_valid():
            form.save()

            return redirect('home')

    context = {'form': form}

    return render(request, 'main/room_form.html', context)


@login_required(login_url='/login')
def delete_room(request, primary_key):
    room = Room.objects.get(id=primary_key)

    if request.user != room.host:
        return HttpResponse("You are not authorized to do that!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'main/delete.html', {'obj': room})


@login_required(login_url='/login')
def delete_message(request, primary_key):
    message = Message.objects.get(id=primary_key)

    if request.user != message.user:
        return HttpResponse("You are not authorized to do that!")

    if request.method == 'POST':
        message.delete()

        return redirect('room', primary_key=message.room.id)

    return render(request, 'main/delete.html', {'obj': message})
