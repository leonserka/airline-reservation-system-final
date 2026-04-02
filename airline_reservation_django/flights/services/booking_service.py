from django.db import transaction, IntegrityError
from ..models import Ticket
from ..constants import SEAT_PRICES, LUGGAGE, EQUIPMENT
from .pdf_service import generate_receipt_pdf
from .email_service import send_receipt_email


def process_booking(user, flight, return_flight, passengers, seat_class,
                    all_selected_seats, total_price, luggage=None, equipment=None):
    try:
        with transaction.atomic():
            flights = [flight]
            if return_flight:
                flights.append(return_flight)
            seat_upgrade  = SEAT_PRICES.get(seat_class, 0)
            luggage_cost  = LUGGAGE.get(luggage, 0) if luggage else 0
            equip_cost    = EQUIPMENT.get(equipment, 0) if equipment else 0
            extras_per_flight = (luggage_cost + equip_cost) / len(flights)

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
                price_per_ticket = float(fl.price) + seat_upgrade + extras_per_flight
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
                        price_paid=round(price_per_ticket, 2),
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

    try:
        pdf_buffer, total_sum = generate_receipt_pdf(
            flight, passengers, seat_class, user, luggage, equipment, return_flight,
            all_selected_seats=all_selected_seats,
        )
    except Exception as e:
        print(f"PDF generation failed: {e}")
        pdf_buffer = None
        total_sum = float(total_price)

    if to_email:
        sent = send_receipt_email(
            to_email=to_email,
            total_sum=total_sum,
            pdf_buffer=pdf_buffer,
            flight=flight,
            user=user,
        )
        print(f"Receipt email to {to_email}: {'sent' if sent else 'failed'}")

    return {"status": "ok"}
