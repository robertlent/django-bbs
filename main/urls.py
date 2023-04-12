from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.home, name="home"),
    path('room/<str:primary_key>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create-room'),
    path('update-room/<str:primary_key>/',
         views.update_room, name='update-room'),
    path('delete-room/<str:primary_key>/',
         views.delete_room, name='delete-room'),
    path('delete-message/<str:primary_key>/',
         views.delete_message, name='delete-message'),
]
