from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Car(models.Model):
    """Individual car available for rent"""
    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    ]
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Maintenance', 'Maintenance'),
    ]
    
    make = models.CharField(max_length=50)  # e.g., Toyota, BMW
    model = models.CharField(max_length=50)  # e.g., Corolla, 3 Series
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=50)
    seats = models.PositiveIntegerField(default=5)
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"
    
    class Meta:
        ordering = ['daily_rate', 'make', 'model']

class Location(models.Model):
    """Represents a rental location/branch"""
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} - {self.city}"

class Booking(models.Model):
    """Reservation or booking for a car"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    booking_number = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    pickup_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='pickup_bookings')
    dropoff_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='dropoff_bookings')
    pickup_date = models.DateTimeField()
    dropoff_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        """Generate a unique booking number on creation"""
        if not self.booking_number:
            self.booking_number = f"B{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total price if not set
        if not self.total_price:
            days = self.get_duration_days()
            self.total_price = self.car.daily_rate * days
            
        super().save(*args, **kwargs)
    
    def get_duration_days(self):
        """Calculate the duration of the booking in days"""
        delta = self.dropoff_date - self.pickup_date
        return delta.days if delta.days > 0 else 1  # Minimum 1 day
    
    def __str__(self):
        return f"Booking #{self.booking_number} - {self.user.username}"

class Review(models.Model):
    """Customer review for a car"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, related_name='review')
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.car}"
    
    class Meta:
        unique_together = ['car', 'user', 'booking']
