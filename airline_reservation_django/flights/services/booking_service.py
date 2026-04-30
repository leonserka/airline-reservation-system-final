from django.db import transaction, IntegrityError
from ..models import Flight, Ticket
from ..constants import SEAT_PRICES, LUGGAGE, EQUIPMENT
from .pdf_service import generate_receipt_pdf
from .email_service import send_receipt_email


def process_booking(user, flight, return_flight, passengers, seat_class,
                    all_selected_seats, luggage=None, equipment=None, currency='EUR'):
    total_sum = 0.0
    try:
        with transaction.atomic():
            requested_flights = [flight]
            if return_flight:
                requested_flights.append(return_flight)

            locked_flights = {
                fl.id: fl for fl in Flight.objects.select_for_update()
                .filter(id__in=[fl.id for fl in requested_flights])
                .order_by("id")
            }
            flights = [locked_flights[fl.id] for fl in requested_flights]

            seat_upgrade  = SEAT_PRICES.get(seat_class, 0)
            luggage_cost  = LUGGAGE.get(luggage, 0) if luggage else 0
            equip_cost    = EQUIPMENT.get(equipment, 0) if equipment else 0
            extras_per_flight = (luggage_cost + equip_cost) / len(flights)

            for fl in flights:
                selected_seats = all_selected_seats.get(str(fl.id), [])
                if len(selected_seats) != len(passengers):
                    return {"status": "error", "msg": "Please select one seat for each passenger."}
                if len(selected_seats) != len(set(selected_seats)):
                    return {"status": "seat_taken", "seat": "duplicate"}
                if fl.available_seats < len(passengers):
                    return {"status": "error", "msg": "Not enough seats are available on this flight."}

                taken_seats = set(
                    Ticket.objects.select_for_update()
                    .filter(
                        flight=fl,
                        status=Ticket.STATUS_BOOKED,
                        seat_number__isnull=False,
                    )
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
                    total_sum += price_per_ticket
                fl.available_seats -= len(passengers)
                fl.save()

    except IntegrityError:
        return {"status": "seat_taken", "seat": "unknown"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

    to_email = user.email or (passengers[0].get("email") if passengers else None)

    try:
        pdf_buffer, _ = generate_receipt_pdf(
            flight, passengers, seat_class, user, luggage, equipment, return_flight,
            all_selected_seats=all_selected_seats,
            currency=currency,
        )
    except Exception as e:
        print(f"PDF generation failed: {e}")
        pdf_buffer = None

    if to_email:
        sent = send_receipt_email(
            to_email=to_email,
            total_sum=total_sum,
            pdf_buffer=pdf_buffer,
            flight=flight,
            user=user,
            currency=currency,
        )
        print(f"Receipt email to {to_email}: {'sent' if sent else 'failed'}")

    return {"status": "ok"}
