
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views import generic
from .models import Car, Location, Booking, Review

from .forms import BookingForm,SearchForm
# Create your views here.

def index(request):
    """Home page view with featured cars and search form"""
    featured_cars = Car.objects.filter(is_featured=True, status='Available')[:3]
    form = SearchForm()
    
    context = {
        'featured_cars': featured_cars,
        'form': form,
    }
    return render(request, 'home.html', context)
def car_list(request):
    """View all available cars with optional filtering"""
    cars = Car.objects.filter(status='Available')
    
    # Filter by make/model
    query = request.GET.get('query')
    if query:
        cars = cars.filter(
            Q(make__icontains=query) | 
            Q(model__icontains=query)
        )
    
    # Filter by location
    location_id = request.GET.get('location')
    if location_id:
        # We'd need to join with Booking model to filter by location properly
        # This is a simplified approach
        location = get_object_or_404(Location, id=location_id)
        
    # Filter by date range
    pickup_date = request.GET.get('pickup_date')
    dropoff_date = request.GET.get('dropoff_date')
    if pickup_date and dropoff_date:
        pickup_date = datetime.strptime(pickup_date, '%Y-%m-%d')
        dropoff_date = datetime.strptime(dropoff_date, '%Y-%m-%d')
        
        # Exclude cars that have bookings overlapping with requested dates
        unavailable_cars = Booking.objects.filter(
            Q(status__in=['Confirmed', 'Active']),
            Q(pickup_date__lte=dropoff_date, dropoff_date__gte=pickup_date)
        ).values_list('car_id', flat=True)
        
        cars = cars.exclude(id__in=unavailable_cars)
    
    context = {
        'cars': cars,
        'locations': Location.objects.all(),
    }
    return render(request, 'car_list.html', context)


def login_view(request) :
    if request.method =='POST' :
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username = username, password = password)
        
        if user not in None :
            login(request,user)
            return redirect('home')
        
        else:
            return messages.success(request,"Invalid login credentials, either your username or password is incorrect")
    return render(request,'auth/login.html')
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def car_detail(request, car_id):
    """View details of a specific car"""
    car = get_object_or_404(Car, id=car_id)
    reviews = car.reviews.all().order_by('-created_at')
    
    # Check availability for next 30 days
    today = timezone.now().date()
    availability = []
    for i in range(30):
        check_date = today + timedelta(days=i)
        bookings = car.bookings.filter(
            status__in=['Confirmed', 'Active'],
            pickup_date__lte=check_date,
            dropoff_date__gte=check_date
        )
        availability.append({
            'date': check_date,
            'available': not bookings.exists()
        })
    
    context = {
        'car': car,
        'reviews': reviews,
        'availability': availability,
        'locations': Location.objects.all(),
    }
    return render(request, 'car_detail.html', context)

def search_cars(request):
    """Search for available cars based on form input"""
    if request.method == 'POST':
        pickup_location = request.POST.get('pickup_location')
        dropoff_location = request.POST.get('dropoff_location')
        pickup_date = request.POST.get('pickup_date')
        dropoff_date = request.POST.get('dropoff_date')
        car_type = request.POST.get('car_type', 'any')
        
        # Build query parameters for car list
        query_params = f"?pickup_location={pickup_location}&dropoff_location={dropoff_location}"
        query_params += f"&pickup_date={pickup_date}&dropoff_date={dropoff_date}"
        if car_type != 'any':
            query_params += f"&car_type={car_type}"
            
        return redirect(f'/cars/{query_params}')
    
    # If GET request, just redirect to car list
    return redirect('car_list')


@login_required
def book_car(request, car_id):
    """Create a new booking for a car"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            pickup_date = form.cleaned_data['pickup_date']
            dropoff_date = form.cleaned_data['dropoff_date']
            pickup_location = form.cleaned_data['pickup_location']
            dropoff_location = form.cleaned_data['dropoff_location']
            
            # Check if car is available for the selected dates
            conflicting_bookings = car.bookings.filter(
                status__in=['Confirmed', 'Active'],
                pickup_date__lte=dropoff_date,
                dropoff_date__gte=pickup_date
            )
            
            if conflicting_bookings.exists():
                messages.error(request, "This car is not available for the selected dates.")
                return redirect('car_detail', car_id=car.id)
            
            # Calculate total price
            delta = dropoff_date - pickup_date
            days = delta.days if delta.days > 0 else 1
            total_price = car.daily_rate * days
            
            # Create booking
            booking = Booking(
                user=request.user,
                car=car,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                pickup_date=pickup_date,
                dropoff_date=dropoff_date,
                total_price=total_price,
                status='Pending'
            )
            booking.save()
            
            messages.success(request, f"Booking created successfully! Your booking number is {booking.booking_number}")
            return redirect('booking_detail', booking_id=booking.id)
    else:
        # Pre-fill form with data from URL parameters if available
        initial_data = {}
        if request.GET.get('pickup_date'):
            initial_data['pickup_date'] = request.GET.get('pickup_date')
        if request.GET.get('dropoff_date'):
            initial_data['dropoff_date'] = request.GET.get('dropoff_date')
        if request.GET.get('pickup_location'):
            initial_data['pickup_location'] = request.GET.get('pickup_location')
        if request.GET.get('dropoff_location'):
            initial_data['dropoff_location'] = request.GET.get('dropoff_location')
            
        form = BookingForm(initial=initial_data)
    
    context = {
        'car': car,
        'form': form,
    }
    return render(request, 'book_car.html', context)

@login_required
def my_bookings(request):
    """View all bookings for the current user"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'my_bookings.html', context)

@login_required
def booking_detail(request, booking_id):
    """View details of a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
    }
    return render(request, 'booking_detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Only allow cancellation of pending or confirmed bookings
    if booking.status not in ['Pending', 'Confirmed']:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'Cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('my_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'cancel_booking.html', context)

