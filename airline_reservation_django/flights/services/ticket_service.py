from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models import Ticket
from .pdf_service import generate_ticket_pdf


def get_user_tickets(user):
    return Ticket.objects.filter(purchased_by=user).select_related("flight").order_by('-id')


def get_ticket(ticket_id, user):
    return get_object_or_404(Ticket, id=ticket_id, purchased_by=user)


def can_cancel(ticket):
    return ticket.seat_class == "PLUS" and ticket.status != "canceled"


@transaction.atomic
def cancel_ticket(ticket):
    if not can_cancel(ticket):
        raise ValueError("You can only cancel PLUS class tickets.")
    flight = ticket.flight
    ticket.status = "canceled"
    ticket.payment_status = "refunded"
    if ticket.seat_number:
        flight.available_seats += 1
        flight.save()
        ticket.seat_number = None
    ticket.save()


def can_download_pdf(ticket):
    return bool(ticket.checked_in) and ticket.status != "canceled"


def verify_checkin_data(ticket, first_name, last_name, id_number):
    if ticket.status == "canceled":
        return False, "Canceled tickets cannot be checked in."
    if not first_name or not last_name or not id_number:
        return False, "Missing data."
    name_matches = first_name.strip().lower() == ticket.passenger_name.lower()
    surname_matches = last_name.strip().lower() == ticket.passenger_surname.lower()
    id_matches = id_number.strip() == ticket.id_number
    if name_matches and surname_matches and id_matches:
        return True, None
    return False, "❌ Entered data does not match our records!"


@transaction.atomic
def mark_checked_in(ticket):
    ticket.checked_in = True
    ticket.checked_in_at = timezone.now()
    ticket.save()
