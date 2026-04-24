import json
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, CharField, Value, Q
from django.db.models.functions import Concat, TruncDate

from django.shortcuts import get_object_or_404
from django.db import transaction
from ..models import Flight, Ticket
from ..services.email_service import send_flight_canceled_email


@login_required
def admin_panel(request):
    if not request.user.is_staff:
        return redirect("home")

    today = date.today()
    total_bookings = Ticket.objects.filter(status=Ticket.STATUS_BOOKED).count()
    total_revenue  = Ticket.objects.filter(status=Ticket.STATUS_BOOKED).aggregate(
        r=Sum("price_paid")
    )["r"] or 0
    active_flights = Flight.objects.filter(date__gte=today).count()
    canceled_count = Ticket.objects.filter(status=Ticket.STATUS_CANCELED).count()
    avg_occupancy  = None

    occ_data = Flight.objects.filter(date__gte=today).aggregate(
        total=Sum("total_seats"), avail=Sum("available_seats")
    )
    if occ_data["total"]:
        booked_seats = occ_data["total"] - occ_data["avail"]
        avg_occupancy = round(booked_seats / occ_data["total"] * 100, 1)

    cutoff = today - timedelta(days=13)
    daily_qs = (
        Ticket.objects
        .filter(created_at__date__gte=cutoff, status=Ticket.STATUS_BOOKED)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"), revenue=Sum("price_paid"))
        .order_by("day")
    )
    day_map = {r["day"]: r for r in daily_qs}
    chart_labels  = []
    chart_bookings = []
    chart_revenue  = []
    for i in range(14):
        d = cutoff + timedelta(days=i)
        chart_labels.append(d.strftime("%b %d"))
        row = day_map.get(d, {})
        chart_bookings.append(row.get("count", 0))
        chart_revenue.append(float(row.get("revenue") or 0))

    top_routes = (
        Ticket.objects
        .filter(status=Ticket.STATUS_BOOKED)
        .annotate(route=Concat(
            "flight__departure_city", Value(" → "),
            "flight__arrival_city", output_field=CharField()
        ))
        .values("route")
        .annotate(bookings=Count("id"), revenue=Sum("price_paid"))
        .order_by("-bookings")[:10]
    )

    flight_search = request.GET.get("flight_search", "").strip()
    flight_date   = request.GET.get("flight_date", "").strip()
    from_city     = request.GET.get("from_city", "").strip()
    to_city       = request.GET.get("to_city", "").strip()

    flights_qs = (
        Flight.objects
        .annotate(booked=F("total_seats") - F("available_seats"))
        .order_by("date", "departure_time")
    )

    if flight_search:
        flights_qs = flights_qs.filter(
            Q(flight_number__icontains=flight_search) |
            Q(departure_city__icontains=flight_search) |
            Q(arrival_city__icontains=flight_search) |
            Q(departure_country__icontains=flight_search) |
            Q(arrival_country__icontains=flight_search)
        )
    if from_city:
        flights_qs = flights_qs.filter(departure_city__icontains=from_city)
    if to_city:
        flights_qs = flights_qs.filter(arrival_city__icontains=to_city)
    if flight_date:
        flights_qs = flights_qs.filter(date=flight_date)
    else:
        flights_qs = flights_qs.filter(date__gte=today)

    flights_occ = flights_qs[:100]
    status_filter = request.GET.get("status", "all")
    qs = Ticket.objects.select_related("flight", "purchased_by").order_by("-id")
    if status_filter == "booked":
        qs = qs.filter(status="booked")
    elif status_filter == "canceled":
        qs = qs.filter(status="canceled")
    reservations = qs[:200]

    return render(request, "flights/admin_panel.html", {
        "page": "panel",
        "total_bookings": total_bookings,
        "total_revenue":  total_revenue,
        "active_flights": active_flights,
        "canceled_count": canceled_count,
        "avg_occupancy":  avg_occupancy,
        "chart_labels":   json.dumps(chart_labels),
        "chart_bookings": json.dumps(chart_bookings),
        "chart_revenue":  json.dumps(chart_revenue),
        "top_routes":     top_routes,
        "flights_occ":    flights_occ,
        "reservations":   reservations,
        "status_filter":  status_filter,
        "flight_search":  flight_search,
        "flight_date":    flight_date,
        "from_city":      from_city,
        "to_city":        to_city,
    })


@login_required
def admin_flight_detail(request, flight_id):
    if not request.user.is_staff:
        return redirect("home")

    flight = get_object_or_404(Flight, id=flight_id)
    tickets = Ticket.objects.filter(flight=flight).select_related("purchased_by").order_by("seat_number")

    booked = tickets.filter(status=Ticket.STATUS_BOOKED).count()
    canceled = tickets.filter(status=Ticket.STATUS_CANCELED).count()
    revenue = tickets.filter(status=Ticket.STATUS_BOOKED).aggregate(r=Sum("price_paid"))["r"] or 0
    fill_pct = round(booked / flight.total_seats * 100, 1) if flight.total_seats else 0

    return render(request, "flights/admin_flight_detail.html", {
        "flight":   flight,
        "tickets":  tickets,
        "booked":   booked,
        "canceled": canceled,
        "revenue":  revenue,
        "fill_pct": fill_pct,
    })


@login_required
@transaction.atomic
def cancel_flight(request, flight_id):
    if not request.user.is_staff:
        return redirect("home")
    if request.method != "POST":
        return redirect("admin_flight_detail", flight_id=flight_id)

    flight = get_object_or_404(Flight, id=flight_id)
    booked_tickets = Ticket.objects.filter(flight=flight, status=Ticket.STATUS_BOOKED)

    for ticket in booked_tickets:
        ticket.status = Ticket.STATUS_CANCELED
        ticket.payment_status = Ticket.PAYMENT_REFUNDED
        ticket.save()
        send_flight_canceled_email(ticket.email, ticket.passenger_name, flight)

    return redirect("admin_panel")
