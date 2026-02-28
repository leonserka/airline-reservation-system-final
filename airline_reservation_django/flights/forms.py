from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Flight, Ticket
from .country_codes import COUNTRY_CODES
from .choices import COUNTRY_CHOICES

class FlightForm(forms.ModelForm):
    departure_country = forms.ChoiceField(
        choices=COUNTRY_CHOICES, label="Departure Country"
    )
    arrival_country = forms.ChoiceField(
        choices=COUNTRY_CHOICES, label="Arrival Country"
    )

    class Meta:
        model = Flight
        fields = [
            "flight_number",
            "departure_country", "departure_city",
            "arrival_country", "arrival_city",
            "date", "departure_time", "arrival_time",
            "price", "total_seats", "available_seats",
            "flight_type",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "departure_time": forms.TimeInput(attrs={"type": "time"}),
            "arrival_time": forms.TimeInput(attrs={"type": "time"}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class PassengerForm(forms.ModelForm):
    country_code = forms.ChoiceField(choices=COUNTRY_CODES)

    class Meta:
        model = Ticket
        fields = [
            "passenger_name",
            "passenger_surname",
            "id_number",
            "country_code",
            "phone_number",
            "email",
        ]
        widgets = {
            "id_number": forms.TextInput(attrs={"maxlength": 11}),
            "email": forms.EmailInput(),
        }