import json
from collections import defaultdict
from django.db.models import Min
from django.shortcuts import render
from ..models import Flight
from ..services.flight_service import future_flights_q

CITY_COORDS = {
    'Zagreb': (45.815, 15.982),
    'Split': (43.508, 16.440),
    'Dubrovnik': (42.650, 18.094),
    'Rijeka': (45.327, 14.441),
    'Zadar': (44.119, 15.232),
    'Osijek': (45.554, 18.695),
    'London': (51.505, -0.091),
    'Paris': (48.856, 2.352),
    'Rome': (41.890, 12.492),
    'Milan': (45.464, 9.190),
    'Berlin': (52.520, 13.405),
    'Amsterdam': (52.370, 4.895),
    'Barcelona': (41.385, 2.173),
    'Madrid': (40.416, -3.703),
    'Vienna': (48.208, 16.373),
    'Prague': (50.075, 14.437),
    'Budapest': (47.498, 19.040),
    'Warsaw': (52.230, 21.012),
    'Brussels': (50.850, 4.352),
    'Zurich': (47.376, 8.541),
    'Lisbon': (38.717, -9.139),
    'Dublin': (53.349, -6.260),
    'Helsinki': (60.192, 24.945),
    'Stockholm': (59.333, 18.065),
    'Oslo': (59.913, 10.752),
    'Copenhagen': (55.676, 12.568),
    'Athens': (37.983, 23.727),
    'Bucharest': (44.426, 26.102),
    'Sofia': (42.697, 23.322),
    'Belgrade': (44.787, 20.457),
    'Ljubljana': (46.056, 14.505),
    'Sarajevo': (43.850, 18.356),
    'Frankfurt': (50.110, 8.682),
    'Munich': (48.137, 11.575),
    'Geneva': (46.204, 6.143),
    'Nice': (43.710, 7.262),
    'Porto': (41.157, -8.629),
    'Valletta': (35.899, 14.514),
    'Riga': (56.946, 24.106),
    'Vilnius': (54.689, 25.279),
    'Tallinn': (59.437, 24.745),
    'Istanbul': (41.015, 28.979),
    'Ankara': (39.925, 32.837),
    'Antalya': (36.896, 30.713),
}

COUNTRY_CODES = {
    'Croatia': 'hr', 'Germany': 'de', 'France': 'fr',
    'Italy': 'it', 'Spain': 'es', 'United Kingdom': 'gb',
    'Netherlands': 'nl', 'Austria': 'at', 'Czech Republic': 'cz',
    'Hungary': 'hu', 'Poland': 'pl', 'Belgium': 'be',
    'Switzerland': 'ch', 'Portugal': 'pt', 'Ireland': 'ie',
    'Finland': 'fi', 'Sweden': 'se', 'Norway': 'no',
    'Denmark': 'dk', 'Greece': 'gr', 'Romania': 'ro',
    'Bulgaria': 'bg', 'Serbia': 'rs', 'Slovenia': 'si',
    'Bosnia and Herzegovina': 'ba', 'Bosnia & Herzegovina': 'ba',
    'Albania': 'al', 'Montenegro': 'me', 'Malta': 'mt',
    'Latvia': 'lv', 'Lithuania': 'lt', 'Estonia': 'ee',
    'Turkey': 'tr', 'Türkiye': 'tr', 'North Macedonia': 'mk',
    'Luxembourg': 'lu', 'Slovakia': 'sk', 'Cyprus': 'cy',
}


def destinations(request):
    dest_qs = (
        Flight.objects
        .filter(future_flights_q())
        .values('arrival_country', 'arrival_city')
        .annotate(min_price=Min('price'))
        .order_by('arrival_country', 'arrival_city')
    )

    by_country = defaultdict(list)
    map_markers = []

    for d in dest_qs:
        country = d['arrival_country'] or 'Unknown'
        city = d['arrival_city']
        min_price = float(d['min_price'])
        by_country[country].append({'city': city, 'min_price': min_price})
        if city in CITY_COORDS:
            lat, lng = CITY_COORDS[city]
            map_markers.append({
                'city': city, 'country': country,
                'lat': lat, 'lng': lng, 'min_price': min_price,
            })

    destinations_by_country = {
        country: {
            'code': COUNTRY_CODES.get(country, ''),
            'cities': cities,
        }
        for country, cities in sorted(by_country.items())
    }

    return render(request, 'flights/destinations.html', {
        'destinations_by_country': destinations_by_country,
        'map_markers_json': json.dumps(map_markers),
    })


def timetable(request):
    flights = Flight.objects.filter(future_flights_q()).order_by('date')

    DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    schedule = defaultdict(lambda: defaultdict(list))
    for f in flights:
        schedule[f.departure_city][f.arrival_city].append(f.date)

    timetable_data = {}
    for dep_city in sorted(schedule.keys()):
        routes = []
        for arr_city in sorted(schedule[dep_city].keys()):
            dates = sorted(schedule[dep_city][arr_city])
            weekdays = sorted(set(d.weekday() for d in dates))
            routes.append({
                'destination': arr_city,
                'period_from': dates[0].strftime('%d %b %Y'),
                'period_to': dates[-1].strftime('%d %b %Y'),
                'days': [DAY_NAMES[d] for d in weekdays],
            })
        timetable_data[dep_city] = routes

    return render(request, 'flights/timetable.html', {'timetable': timetable_data})


def seat_classes(request):
    return render(request, 'flights/seat_classes.html')


def travel_documents(request):
    return render(request, 'flights/travel_documents.html')


def baggage(request):
    return render(request, 'flights/baggage.html')


def about_company(request):
    return render(request, 'flights/about_company.html')


def media(request):
    return render(request, 'flights/media.html')


def special_categories(request):
    return render(request, 'flights/special_categories.html')


def help_page(request):
    return render(request, 'flights/help.html')


def special_offers(request):
    cheapest = (
        Flight.objects
        .filter(future_flights_q(), available_seats__gt=0)
        .order_by('?')[:9]
    )
    return render(request, 'flights/special_offers.html', {'offers': cheapest})
