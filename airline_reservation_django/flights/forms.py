from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Flight, Ticket, UserProfile
from .country_codes import COUNTRY_CODES
from .choices import COUNTRY_CHOICES


class FlightForm(forms.ModelForm):
    departure_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="Departure Country")
    arrival_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="Arrival Country")

    class Meta:
        model = Flight
        fields = [
            "flight_number",
            "departure_country", "departure_city", "departure_timezone",
            "arrival_country", "arrival_city", "arrival_timezone",
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


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email":      forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["date_of_birth", "phone_number", "country"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "phone_number":  forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. +385 91 234 5678"}),
            "country":       forms.Select(
                attrs={"class": "form-control"},
                choices=[("", "— Select country —")] + list(COUNTRY_CHOICES),
            ),
        }


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
