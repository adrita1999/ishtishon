"""Ishtishon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
<<<<<<< Updated upstream
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home') #test
=======
    1. Add an import:  from my_app import views 7 no line change
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
>>>>>>> Stashed changes
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
#import hr.views as hr_views
import rs.views as rs_views

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('jobs', hr_views.list_jobs),
    path('trains', rs_views.list_trains, name= 'train'),
    path('stations', rs_views.list_stations, name= 'station'),
    path('',rs_views.homepage,name= 'home'),
    path('registration',rs_views.registration,name= 'register'),
    path('login',rs_views.login,name= 'login'),
    path('seat_selection',rs_views.seatselection,name= 'seat_selection'),
    path('updateinfo',rs_views.updateinfo,name= 'updateinfo'),
    #hr delete hoyna


]
