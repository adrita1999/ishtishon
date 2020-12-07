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
    path('',rs_views.homepage,name= 'home'),
    path('registration',rs_views.registration,name= 'register'),
    path('login',rs_views.login,name= 'login'),
    path('seat_selection',rs_views.seatselection,name= 'seat_selection'),
    path('updateinfo',rs_views.updateinfo,name= 'updateinfo'),
    path('changepass',rs_views.changepass,name= 'changepass'),
    path('changemail',rs_views.changemail,name= 'changemail'),
    path('changenum',rs_views.changenum,name= 'changenum'),
    path('prev',rs_views.prev,name= 'prev'),
    path('upcoming',rs_views.upcoming,name= 'upcoming'),
    path('contactus',rs_views.contactus,name= 'contactus'),
    path('successful',rs_views.successful,name= 'successful'),
    path('payment_selection',rs_views.payment_selection,name= 'payment_selection'),
    path('bkash_payment',rs_views.bkash,name= 'bkash_payment'),
    path('card_payment',rs_views.card,name= 'card_payment'),
    path('nexus_payment',rs_views.nexus,name= 'nexus_payment'),
    path('rocket_payment',rs_views.rocket,name= 'rocket_payment'),
    path('Ticket',rs_views.pdf,name='ticket'),
    path('forget_pass',rs_views.forgetpass,name='forget_pass'),
    path('forget_pass_change',rs_views.forgetchangepass,name='forget_pass_change'),
    path('demo',rs_views.demo,name='demo'),

    #hr delete hoyna


]
