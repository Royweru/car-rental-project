// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const carList = document.querySelector('#car-list');
    const bookingForm = document.querySelector('#booking-form');

    // Example function to handle form submission
    function handleBooking(event) {
        event.preventDefault();
        console.log('Booking submitted');
    }

    // Example function to display cars
    function displayCars() {
        console.log('Displaying cars');
    }

    // Add event listeners
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleBooking);
    }

    // Initialize the page
    displayCars();
});