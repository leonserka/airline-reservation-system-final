import base64
import os
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS


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
                         luggage=None, equipment=None, return_flight=None):
    from ..constants import SEAT_PRICES, LUGGAGE, EQUIPMENT

    seat_upgrade      = SEAT_PRICES.get(seat_class, 0)
    luggage_cost      = LUGGAGE.get(luggage, 0) if luggage else 0
    equip_cost        = EQUIPMENT.get(equipment, 0) if equipment else 0
    num_flights       = 2 if return_flight else 1
    extras_per_flight = (luggage_cost + equip_cost) / num_flights
    price_per_ticket  = float(flight.price) + seat_upgrade + extras_per_flight

    rows = []
    total_sum = 0.0

    for p in passengers:
        rows.append({
            "name": f"{p['passenger_name']} {p['passenger_surname']}",
            "seat": p.get("seat_number", "N/A"),
            "class": seat_class,
            "price": f"{price_per_ticket:.2f}",
        })
        total_sum += price_per_ticket

    if return_flight:
        ret_price_per_ticket = float(return_flight.price) + seat_upgrade + extras_per_flight
        total_sum += ret_price_per_ticket * len(passengers)

    context = {
        "flight": flight,
        "passengers": rows,
        "user": user,
        "total_sum": f"{total_sum:.2f}",
        "date_today": datetime.now().strftime("%d/%m/%Y"),
        "order_number": datetime.now().strftime("%Y%m%d-%H%M%S"),
    }

    html = render_to_string("flights/receipt_pdf_template.html", context)
    css_path = os.path.join(settings.BASE_DIR, "flights", "static", "flights", "css", "receipt_pdf.css")
    stylesheets = [CSS(css_path)] if os.path.exists(css_path) else []
    return BytesIO(HTML(string=html).write_pdf(stylesheets=stylesheets)), total_sum
