from .flights import home, create_flight, flight_list
from .currency import set_currency
from .pages import destinations, timetable, seat_classes, travel_documents, baggage, special_categories, help_page, special_offers, about_company, media
from .auth import register, custom_logout, profile, PasswordResetConfirmWithEmail
from .admin_views import admin_panel, admin_flight_detail, cancel_flight
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
    check_in,
    resend_receipt,
)
