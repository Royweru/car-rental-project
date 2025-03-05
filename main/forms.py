from django import forms
from .models import Booking, Review, Location

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
            'pickup_date': DateTimeInput(),
            'dropoff_date': DateTimeInput(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        pickup_date = cleaned_data.get('pickup_date')
        dropoff_date = cleaned_data.get('dropoff_date')
        
        if pickup_date and dropoff_date:
            # Ensure pickup date is not in the past
            if pickup_date < timezone.now():
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

class SearchForm(forms.Form):
    pickup_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label="Select pickup location",
        required=True
    )
    dropoff_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label="Select drop-off location",
        required=True
    )
    pickup_date = forms.DateTimeField(
        widget=DateTimeInput(),
        required=True
    )
    dropoff_date = forms.DateTimeField(
        widget=DateTimeInput(),
        required=True
    )
    car_type = forms.ChoiceField(
        choices=[
            ('any', 'Any type'),
            ('economy', 'Economy'),
            ('compact', 'Compact'),
            ('midsize', 'Midsize'),
            ('suv', 'SUV'),
            ('luxury', 'Luxury'),
        ],
        required=False,
        initial='any'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        pickup_date = cleaned_data.get('pickup_date')
        dropoff_date = cleaned_data.get('dropoff_date')
        
        if pickup_date and dropoff_date:
            # Ensure pickup date is not in the past
            if pickup_date < timezone.now():
                self.add_error('pickup_date', "Pickup date cannot be in the past.")
            
            # Ensure dropoff date is after pickup date
            if dropoff_date <= pickup_date:
                self.add_error('dropoff_date', "Drop-off date must be after pickup date.")
        
        return cleaned_data