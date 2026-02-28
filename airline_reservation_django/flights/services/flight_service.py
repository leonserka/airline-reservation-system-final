from datetime import datetime, date
from ..models import Flight


def _distinct_list(field, **filters):
    return list(Flight.objects.filter(**filters).values_list(field, flat=True).distinct())


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
                departure_city=arr_city, arrival_city=dep_city, date=ret_date, date__gte=today
            )

    return {"flights": flights, "return_flights": returns, "show_results": show_results}


def get_origin_countries():
    return _distinct_list("departure_country")


def get_airports_by_country(country):
    return _distinct_list("departure_city", departure_country=country)


def get_destination_countries(origin_country, origin_city):
    return _distinct_list("arrival_country", departure_country=origin_country, departure_city=origin_city)


def get_destination_airports(origin_country, origin_city, dest_country):
    return _distinct_list(
        "arrival_city",
        departure_country=origin_country,
        departure_city=origin_city,
        arrival_country=dest_country,
    )


def get_available_dates_for_route(dep_city, arr_city, route_type="departure"):
    today = date.today()
    if not dep_city or not arr_city:
        return []
    if route_type == "departure":
        qs = Flight.objects.filter(departure_city=dep_city, arrival_city=arr_city, date__gte=today)
    else:
        qs = Flight.objects.filter(departure_city=arr_city, arrival_city=dep_city, date__gte=today)
    return sorted(set(d.strftime("%Y-%m-%d") for d in qs.values_list("date", flat=True).distinct()))
