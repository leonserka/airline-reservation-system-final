from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models import Ticket


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
