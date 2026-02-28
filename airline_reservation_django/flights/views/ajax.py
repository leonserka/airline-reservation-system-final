from django.http import JsonResponse
from ..services import flight_service


def get_origin_countries(request):
    return JsonResponse(flight_service.get_origin_countries(), safe=False)


def get_airports_by_country(request):
    return JsonResponse(flight_service.get_airports_by_country(request.GET.get("country")), safe=False)


def get_destination_countries(request):
    return JsonResponse(
        flight_service.get_destination_countries(request.GET.get("origin_country"), request.GET.get("origin_city")),
        safe=False,
    )


def get_destination_airports(request):
    return JsonResponse(
        flight_service.get_destination_airports(
            request.GET.get("origin_country"),
            request.GET.get("origin_city"),
            request.GET.get("dest_country"),
        ),
        safe=False,
    )


def get_available_dates(request):
    return JsonResponse(
        flight_service.get_available_dates_for_route(
            request.GET.get("departure_city"),
            request.GET.get("arrival_city"),
            request.GET.get("type", "departure"),
        ),
        safe=False,
    )
