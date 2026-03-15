from datetime import datetime, date
from ..models import Flight


def valid_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def search(dep_city, arr_city, dep_date_str, ret_date_str):
    today = date.today()
    dep_date = valid_date(dep_date_str)
    ret_date = valid_date(ret_date_str)
    flights = Flight.objects.none()
    returns = Flight.objects.none()
    show_results = False

    if dep_city and arr_city:
        show_results = True
        base = Flight.objects.filter(departure_city=dep_city, arrival_city=arr_city, date__gte=today)
        flights = base.filter(date=dep_date) if dep_date else base
        if ret_date:
            returns = Flight.objects.filter(
                departure_city=arr_city,
                arrival_city=dep_city,
                date=ret_date,
                date__gte=today,
            )

    return {"flights": flights, "return_flights": returns, "show_results": show_results}


def get_origin_countries():
    return list(Flight.objects.values_list("departure_country", flat=True).distinct())


def get_airports_by_country(country):
    return list(Flight.objects.filter(departure_country=country).values_list("departure_city", flat=True).distinct())


def get_destination_countries(origin_country, origin_city):
    return list(
        Flight.objects
        .filter(departure_country=origin_country, departure_city=origin_city)
        .values_list("arrival_country", flat=True)
        .distinct()
    )


def get_destination_airports(origin_country, origin_city, dest_country):
    return list(
        Flight.objects
        .filter(departure_country=origin_country, departure_city=origin_city, arrival_country=dest_country)
        .values_list("arrival_city", flat=True)
        .distinct()
    )


def get_available_dates_for_route(dep_city, arr_city, route_type="departure"):
    today = date.today()
    if not dep_city or not arr_city:
        return []

    if route_type == "departure":
        flights = Flight.objects.filter(departure_city=dep_city, arrival_city=arr_city, date__gte=today)
    else:
        flights = Flight.objects.filter(departure_city=arr_city, arrival_city=dep_city, date__gte=today)

    all_dates = flights.values_list("date", flat=True).distinct()
    return sorted(set(d.strftime("%Y-%m-%d") for d in all_dates))
