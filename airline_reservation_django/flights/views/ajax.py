from django.http import JsonResponse
from ..services import flight_service


def get_origin_countries(request):
    countries = flight_service.get_origin_countries()
    return JsonResponse(countries, safe=False)


def get_airports_by_country(request):
    country = request.GET.get("country")
    cities = flight_service.get_airports_by_country(country)
    return JsonResponse(cities, safe=False)


def get_destination_countries(request):
    origin_country = request.GET.get("origin_country")
    origin_city = request.GET.get("origin_city")
    countries = flight_service.get_destination_countries(origin_country, origin_city)
    return JsonResponse(countries, safe=False)


def get_destination_airports(request):
    origin_country = request.GET.get("origin_country")
    origin_city = request.GET.get("origin_city")
    dest_country = request.GET.get("dest_country")
    cities = flight_service.get_destination_airports(origin_country, origin_city, dest_country)
    return JsonResponse(cities, safe=False)


def get_available_dates(request):
    departure_city = request.GET.get("departure_city")
    arrival_city = request.GET.get("arrival_city")
    route_type = request.GET.get("type", "departure")
    dates = flight_service.get_available_dates_for_route(departure_city, arrival_city, route_type)
    return JsonResponse(dates, safe=False)
