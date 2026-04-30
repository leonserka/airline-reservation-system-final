from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from ..forms import FlightForm
from ..models import Flight
from ..services.flight_service import search


def home(request):
    return render(request, "flights/home.html")


@login_required
def create_flight(request):
    if not request.user.is_staff:
        return redirect("home")
    form = FlightForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("flight_list")
    return render(request, "flights/create_flight.html", {"form": form})


@login_required
def flight_list(request):
    dep = request.GET.get("departure_city")
    arr = request.GET.get("arrival_city")
    dep_date = request.GET.get("departure_date")
    ret_date = request.GET.get("return_date")
    search_data = search(dep, arr, dep_date, ret_date)

    today = date.today()
    cheapest = list(
        Flight.objects
        .filter(date__gte=today, available_seats__gt=0)
        .order_by('?')[:6]
    )

    popular_routes = list(
        Flight.objects
        .filter(date__gte=today, available_seats__gt=0)
        .values('departure_city', 'arrival_city')
        .annotate(min_price=Min('price'))
        .order_by('?')[:10]
    )

    search_data['cheapest_flights'] = cheapest
    search_data['popular_routes'] = popular_routes
    return render(request, "flights/flight_list.html", search_data)
