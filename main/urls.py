from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('room/<str:primary_key>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create-room'),
    path('update-room/<str:primary_key>/',
         views.update_room, name='update-room'),
    path('delete-room/<str:primary_key>/',
         views.delete_room, name='delete-room'),
]
