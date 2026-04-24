from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..models import Ticket
from ..services.email_service import send_checkin_email, send_receipt_email
from ..services.pdf_service import generate_receipt_pdf
from ..services.ticket_service import (
    get_user_tickets,
    get_ticket,
    can_cancel,
    cancel_ticket,
    can_download_pdf,
    get_checkin_button_state,
    verify_checkin_data,
    mark_checked_in,
)
from ..services.pdf_service import generate_ticket_pdf


@login_required
def check_booked_flights(request):
    all_tickets = get_user_tickets(request.user)
    today = date.today()
    active_tickets = [t for t in all_tickets if t.flight.date >= today]
    past_tickets   = [t for t in all_tickets if t.flight.date < today]
    return render(request, "flights/check_booked_flights.html", {
        "active_tickets": active_tickets,
        "past_tickets": past_tickets,
    })


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

    if request.GET.get("download") == "pdf":
        if not can_download_pdf(ticket):
            return HttpResponse(
                "❌ You must complete check-in before downloading your boarding pass.",
                status=403,
            )
        pdf_buffer = generate_ticket_pdf(ticket)
        return HttpResponse(
            pdf_buffer.getvalue(),
            content_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="ticket_{ticket.id}.pdf"'},
        )

    return render(request, "flights/about_ticket.html", {
        "ticket": ticket,
        "can_cancel": can_cancel(ticket),
        "checkin_state": get_checkin_button_state(ticket),
    })


@login_required
def check_in(request, ticket_id):
    ticket = get_ticket(ticket_id, request.user)

    if ticket.status == Ticket.STATUS_CANCELED:
        return render(request, "flights/error.html", {"message": "Canceled tickets cannot be checked in."})

    if ticket.flight.date < date.today():
        return render(request, "flights/error.html", {"message": "Check-in is not available for past flights."})

    if ticket.checked_in:
        return redirect("about_ticket", ticket_id=ticket.id)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        id_number = request.POST.get("id_number")

        ok, error = verify_checkin_data(ticket, first_name, last_name, id_number)

        if ok:
            mark_checked_in(ticket)
            send_checkin_email(ticket.email, ticket.flight.flight_number)
            return redirect("about_ticket", ticket_id=ticket.id)

        return render(request, "flights/check_in.html", {"ticket": ticket, "error": error})

    return render(request, "flights/check_in.html", {"ticket": ticket})


@login_required
def resend_receipt(request, ticket_id):
    ticket = get_ticket(ticket_id, request.user)
    window = timedelta(seconds=3)
    outbound_tickets = list(Ticket.objects.filter(
        purchased_by=request.user,
        flight=ticket.flight,
        created_at__range=(ticket.created_at - window, ticket.created_at + window),
    ))

    return_tickets = list(Ticket.objects.filter(
        purchased_by=request.user,
        created_at__range=(ticket.created_at - window, ticket.created_at + window),
    ).exclude(flight=ticket.flight))

    return_flight = return_tickets[0].flight if return_tickets else None

    passengers = [{
        "passenger_name": t.passenger_name,
        "passenger_surname": t.passenger_surname,
        "id_number": t.id_number,
        "email": t.email,
        "phone_number": t.phone_number,
        "country_code": t.country_code,
    } for t in outbound_tickets]

    all_selected_seats = {}
    for t in outbound_tickets + return_tickets:
        fid = str(t.flight_id)
        if fid not in all_selected_seats:
            all_selected_seats[fid] = []
        if t.seat_number:
            all_selected_seats[fid].append(t.seat_number)

    try:
        pdf_buffer, total_sum = generate_receipt_pdf(
            ticket.flight, passengers, ticket.seat_class, request.user,
            ticket.extra_luggage, ticket.extra_equipment, return_flight,
            all_selected_seats=all_selected_seats,
        )
        to_email = request.user.email or ticket.email
        send_receipt_email(
            to_email=to_email,
            total_sum=total_sum,
            pdf_buffer=pdf_buffer,
            flight=ticket.flight,
            user=request.user,
        )
        messages.success(request, f"Receipt resent to {to_email}.")
    except Exception as e:
        messages.error(request, f"Could not resend receipt: {e}")

    return redirect("about_ticket", ticket_id=ticket.id)
