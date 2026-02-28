from .flights import home, create_flight, flight_list
from .auth import register, custom_logout
from .ajax import (
    get_origin_countries,
    get_airports_by_country,
    get_destination_countries,
    get_destination_airports,
    get_available_dates,
)
from .booking import (
    book_step1,
    book_step2,
    book_step3,
    book_step4,
    book_step5,
    book_success,
)
from .tickets import (
    check_booked_flights,
    cancel_booked_flight,
    about_ticket,
)
