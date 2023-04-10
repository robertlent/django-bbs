from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Room, Topic
from .forms import RoomForm


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
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

    context = {}

    return render(request, 'main/login_register.html', context)


def logout_user(request):
    logout(request)

    return redirect('home')


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

    context = {'room': room}

    return render(request, 'main/room.html', context)


def create_room(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('home')

    context = {'form': form}

    return render(request, 'main/room_form.html', context)


def update_room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    form = RoomForm(instance=room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)

        if form.is_valid():
            form.save()

            return redirect('home')

    context = {'form': form}

    return render(request, 'main/room_form.html', context)


def delete_room(request, primary_key):
    room = Room.objects.get(id=primary_key)

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'main/delete.html', {'obj': room})
