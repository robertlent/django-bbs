from django.shortcuts import render, redirect
from .models import Room
from .forms import RoomForm


def home(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}

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
