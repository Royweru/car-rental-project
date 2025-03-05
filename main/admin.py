from django.contrib import admin
from .models import Car,Booking,Review,Location
# Register your models here.

admin.site.register(Car)

admin.site.register(Booking)

admin.site.register(Review)

admin.site.register(Location)
