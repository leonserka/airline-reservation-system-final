from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..services.ticket_service import (
    get_user_tickets,
    get_ticket,
    can_cancel,
    cancel_ticket,
)


@login_required
def check_booked_flights(request):
    tickets = get_user_tickets(request.user)
    return render(request, "flights/check_booked_flights.html", {"tickets": tickets})


@login_required
def cancel_booked_flight(request, ticket_id):
    ticket = get_ticket(ticket_id, request.user)
    try:
        cancel_ticket(ticket)
    except ValueError as e:
        return render(request, "flights/error.html", {"message": str(e)})
    return redirect("check_booked_flights")


@login_required
def about_ticket(request, ticket_id):
    ticket = get_ticket(ticket_id, request.user)
    return render(request, "flights/about_ticket.html", {"ticket": ticket, "can_cancel": can_cancel(ticket)})
