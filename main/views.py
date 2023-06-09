from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

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
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

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
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}

    return render(request, 'main/home.html', context)


def room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        room.participants.add(request.user)

        return redirect('room', primary_key=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}

    return render(request, 'main/room.html', context)


def user_profile(request, primary_key):
    user = User.objects.get(id=primary_key)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}

    return render(request, 'main/profile.html', context)


@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        return redirect('home')

    context = {'form': form, 'topics': topics}

    return render(request, 'main/room_form.html', context)


@login_required(login_url='/login')
def update_room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not authorized to do that!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}

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

        if not Message.objects.filter(user_id=message.user.id, room_id=message.room.id):
            message.room.participants.remove(message.user.id)

        return redirect('room', primary_key=message.room.id)

    return render(request, 'main/delete.html', {'obj': message})


@login_required(login_url='/login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()

            return redirect('user-profile', primary_key=user.id)

    return render(request, 'main/update-user.html', {'form': form})


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    return render(request, 'main/topics.html', {'topics': topics})


def activity_page(request):
    room_messages = Message.objects.all()

    return render(request, 'main/activity.html', {'room_messages': room_messages})
