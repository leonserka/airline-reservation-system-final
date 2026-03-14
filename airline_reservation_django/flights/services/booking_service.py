import logging
from django.db import transaction, IntegrityError
from ..models import Ticket
from .pdf_service import generate_receipt_pdf
from .email_service import send_receipt_email

logger = logging.getLogger(__name__)


def process_booking(user, flight, return_flight, passengers, seat_class,
                    all_selected_seats, total_price, luggage=None, equipment=None):

    try:
        with transaction.atomic():
            flights = [flight]
            if return_flight:
                flights.append(return_flight)

            for fl in flights:
                selected_seats = all_selected_seats.get(str(fl.id), [])
                taken_seats = set(
                    Ticket.objects.select_for_update()
                    .filter(flight=fl)
                    .values_list("seat_number", flat=True)
                )
                for seat in selected_seats:
                    if seat in taken_seats:
                        return {"status": "seat_taken", "seat": seat}

            for fl in flights:
                seats = all_selected_seats.get(str(fl.id), [])
                for i, pax in enumerate(passengers):
                    seat = seats[i] if i < len(seats) else None
                    Ticket.objects.create(
                        flight=fl,
                        passenger_name=pax["passenger_name"],
                        passenger_surname=pax["passenger_surname"],
                        id_number=pax["id_number"],
                        email=pax["email"],
                        phone_number=pax["phone_number"],
                        country_code=pax["country_code"],
                        seat_class=seat_class,
                        seat_number=seat,
                        price_paid=fl.price,
                        payment_method="PayPal",
                        purchased_by=user,
                        extra_luggage=luggage,
                        extra_equipment=equipment,
                    )
                fl.available_seats -= len(passengers)
                fl.save()

    except IntegrityError:
        return {"status": "seat_taken", "seat": "unknown"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

    to_email = user.email or (passengers[0].get("email") if passengers else None)
    total_sum = float(total_price)

    try:
        pdf_buffer, total_sum = generate_receipt_pdf(flight, passengers, seat_class, user)
    except Exception as e:
        logger.error("PDF generation failed: %s", e, exc_info=True)
        pdf_buffer = None

    if to_email:
        sent = send_receipt_email(
            to_email=to_email,
            total_sum=total_sum,
            pdf_buffer=pdf_buffer,
            flight=flight,
            user=user,
        )
        logger.info("Receipt email to %s: %s", to_email, "sent" if sent else "failed")

    return {"status": "ok"}
