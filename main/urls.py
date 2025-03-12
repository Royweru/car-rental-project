from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
  path('',views.index,name='home') ,
  
     path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('search/', views.search_cars, name='search_cars'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
     path('cars/', views.car_list, name='car_list'),
     
    path('cars/<int:car_id>/book/', views.book_car, name='book_car'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]