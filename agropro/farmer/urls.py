from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("",views.profile,name='profile'),
    path("profile",views.profile,name='profile'),
    path("acceptnotif/",views.acceptNotif,name='acceptNotif'),
    path("notifications/",views.notification,name='notification'),
    path("prediction",views.prediction,name='prediction'),
    path("editProfile",views.editProfile,name='editProfile'),
    path("setCrop",views.setCrop,name='setCrop'),
    path("removeCrop/<int:crop_id>",views.removeCrop,name='removeCrop')
]