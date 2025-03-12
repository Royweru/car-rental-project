
from django import forms
from django.utils import timezone 
from .models import Booking, Review, Location
from datetime import date
class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['pickup_location', 'dropoff_location', 'pickup_date', 'dropoff_date']
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}),
            'dropoff_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pickup_date = cleaned_data.get('pickup_date')
        dropoff_date = cleaned_data.get('dropoff_date')

        # Convert to date if it's a datetime
        if pickup_date and hasattr(pickup_date, 'date'):
            pickup_date = pickup_date.date()
        if dropoff_date and hasattr(dropoff_date, 'date'):
            dropoff_date = dropoff_date.date()

        if pickup_date and dropoff_date:
            # Use date.today() to get today's date
            if pickup_date < date.today():
                self.add_error('pickup_date', "Pickup date cannot be in the past.")

            # Ensure dropoff date is after pickup date
            if dropoff_date <= pickup_date:
                self.add_error('dropoff_date', "Drop-off date must be after pickup date.")

        return cleaned_data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this car'}),
        }

class CarSearchForm(forms.Form):
    TRANSMISSION_CHOICES = [
        ('', 'Any Transmission'),
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    ]

    SEATS_CHOICES = [
        ('', 'Any Number of Seats'),
        ('4', '4 Seats'),
        ('5', '5 Seats'),
        ('7', '7 Seats'),
    ]

    make = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Car Make (e.g., Toyota, BMW)'
        })
    )

    model = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Car Model (e.g., Corolla, X5)'
        })
    )

    transmission = forms.ChoiceField(
        choices=TRANSMISSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    seats = forms.ChoiceField(
        choices=SEATS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Minimum Daily Rate'
        })
    )

    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Maximum Daily Rate'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        # Validate price range
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError("Minimum price cannot be higher than maximum price.")

        return cleaned_data