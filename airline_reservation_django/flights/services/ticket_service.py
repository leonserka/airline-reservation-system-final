from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models import Ticket


def get_user_tickets(user):
    return Ticket.objects.filter(purchased_by=user).select_related("flight").order_by('-id')


def get_ticket(ticket_id, user):
    return get_object_or_404(Ticket, id=ticket_id, purchased_by=user)


def can_cancel(ticket):
    return ticket.seat_class == "PLUS" and ticket.status != Ticket.STATUS_CANCELED


@transaction.atomic
def cancel_ticket(ticket):
    if not can_cancel(ticket):
        raise ValueError("You can only cancel PLUS class tickets.")
    flight = ticket.flight
    ticket.status = Ticket.STATUS_CANCELED
    ticket.payment_status = Ticket.PAYMENT_REFUNDED
    if ticket.seat_number:
        flight.available_seats += 1
        flight.save()
        ticket.seat_number = None
    ticket.save()


def can_download_pdf(ticket):
    return bool(ticket.checked_in) and ticket.status != Ticket.STATUS_CANCELED


def get_checkin_button_state(ticket):
    if ticket.status == Ticket.STATUS_CANCELED:
        return "canceled"
    if ticket.checked_in:
        return "checked_in"
    now = timezone.now()
    time_until = ticket.flight.departure_datetime - now
    if time_until > timedelta(hours=24):
        return "too_early"
    if time_until < timedelta(hours=2):
        return "too_late"
    return "open"


def verify_checkin_data(ticket, first_name, last_name, id_number):
    if ticket.status == Ticket.STATUS_CANCELED:
        return False, "Canceled tickets cannot be checked in."

    now = timezone.now()
    time_until = ticket.flight.departure_datetime - now
    if time_until > timedelta(hours=24):
        opens_at = (ticket.flight.departure_datetime - timedelta(hours=24)).strftime("%b %d at %H:%M")
        return False, f"Check-in is not yet open. Online check-in opens on {opens_at}."
    if time_until < timedelta(hours=2):
        return False, "Online check-in is closed (less than 2 hours before departure)."

    if not first_name or not last_name or not id_number:
        return False, "Missing data."
    if (first_name.strip().lower() == ticket.passenger_name.lower()
            and last_name.strip().lower() == ticket.passenger_surname.lower()
            and id_number.strip() == ticket.id_number):
        return True, None
    return False, "❌ Entered data does not match our records!"


@transaction.atomic
def mark_checked_in(ticket):
    ticket.checked_in = True
    ticket.checked_in_at = timezone.now()
    ticket.save()
