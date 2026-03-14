from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..services.email_service import send_checkin_email
from ..services.ticket_service import (
    get_user_tickets,
    get_ticket,
    can_cancel,
    cancel_ticket,
    can_download_pdf,
    verify_checkin_data,
    mark_checked_in,
)
from ..services.pdf_service import generate_ticket_pdf


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
    })


@login_required
def check_in(request, ticket_id):
    ticket = get_ticket(ticket_id, request.user)

    if ticket.status == "canceled":
        return render(request, "flights/error.html", {"message": "Canceled tickets cannot be checked in."})

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
