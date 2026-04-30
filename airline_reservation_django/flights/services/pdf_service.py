import base64
import os
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
from ..constants import SEAT_PRICES, LUGGAGE, EQUIPMENT
from .currency_service import format_price, get_rates

def generate_ticket_pdf(ticket):
    departure_local = ticket.flight.departure_datetime.strftime("%Y-%m-%d %H:%M")
    arrival_local = ticket.flight.arrival_datetime.strftime("%Y-%m-%d %H:%M")

    qr_img = qrcode.make(f"TICKET-{ticket.id}-{ticket.flight.flight_number}")
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode()
    gate_closes = (ticket.flight.departure_datetime - timedelta(minutes=30)).strftime("%H:%M")

    context = {
        "ticket": ticket,
        "departure_local": departure_local,
        "arrival_local": arrival_local,
        "qr_base64": qr_base64,
        "gate_closes": gate_closes,
    }

    html = render_to_string("flights/ticket_pdf_template.html", context)
    css_path = os.path.join(settings.BASE_DIR, "flights", "static", "flights", "css", "ticket_pdf.css")
    return BytesIO(HTML(string=html).write_pdf(stylesheets=[CSS(css_path)]))


def generate_receipt_pdf(flight, passengers, seat_class, user,
                         luggage=None, equipment=None, return_flight=None,
                         all_selected_seats=None, currency='EUR'):

    flights = [flight]
    if return_flight:
        flights.append(return_flight)

    seat_upgrade      = SEAT_PRICES.get(seat_class, 0)
    luggage_cost      = LUGGAGE.get(luggage, 0) if luggage else 0
    equip_cost        = EQUIPMENT.get(equipment, 0) if equipment else 0
    extras_per_flight = (luggage_cost + equip_cost) / len(flights)

    rows = []
    total_sum = 0.0

    for fl in flights:
        seats = (all_selected_seats or {}).get(str(fl.id), [])
        price_per_ticket = float(fl.price) + seat_upgrade + extras_per_flight
        for i, p in enumerate(passengers):
            seat = seats[i] if i < len(seats) else "N/A"
            rows.append({
                "flight": f"{fl.departure_city} → {fl.arrival_city}",
                "name": f"{p['passenger_name']} {p['passenger_surname']}",
                "seat": seat,
                "class": seat_class,
                "price": format_price(price_per_ticket, currency),
            })
            total_sum += price_per_ticket

    context = {
        "outbound_flight": flight,
        "return_flight": return_flight,
        "passengers": rows,
        "seat_class": seat_class,
        "user": user,
        "total_sum": format_price(total_sum, currency),
        "currency": currency,
        "date_today": datetime.now().strftime("%d/%m/%Y"),
        "order_number": datetime.now().strftime("%Y%m%d-%H%M%S"),
    }

    html = render_to_string("flights/receipt_pdf_template.html", context)
    css_path = os.path.join(settings.BASE_DIR, "flights", "static", "flights", "css", "receipt_pdf.css")
    stylesheets = [CSS(css_path)] if os.path.exists(css_path) else []
    return BytesIO(HTML(string=html).write_pdf(stylesheets=stylesheets)), total_sum
