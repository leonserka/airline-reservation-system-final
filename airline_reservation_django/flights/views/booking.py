from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
import json
import requests as http_requests
from ..models import Flight, Ticket
from ..forms import PassengerForm
from ..constants import SEAT_PRICES, LUGGAGE, EQUIPMENT
from ..services.seatmap_service import build_seat_positions
from ..services.booking_service import process_booking
from ..services.booking_session import BookingSession
from ..services.currency_service import get_rates


def capture_paypal_order(order_id):
    auth = http_requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=15,
    )
    auth.raise_for_status()
    access_token = auth.json()["access_token"]

    capture = http_requests.post(
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        timeout=15,
    )
    return capture.json()


def get_return_flight(bs):
    rid = bs.get_return_flight_id()
    return Flight.objects.filter(id=rid).first() if rid else None


@login_required
def book_step1(request, flight_id):
    bs = BookingSession(request)
    flight = get_object_or_404(Flight, id=flight_id)

    bs.set_outbound_flight_id(flight.id)

    if request.GET.get("return_id"):
        bs.set_return_flight_id(request.GET.get("return_id"))

    return_flight = get_return_flight(bs)
    num_passengers = int(request.GET.get("pax", bs.get_num_passengers()))

    if request.method == "POST":
        forms = [PassengerForm(request.POST, prefix=str(i)) for i in range(num_passengers)]
        if all(f.is_valid() for f in forms):
            bs.set_passengers([f.cleaned_data for f in forms])
            bs.set_num_passengers(num_passengers)
            return redirect("book_step2", flight_id=flight.id)
    else:
        forms = [
            PassengerForm(prefix=str(i), initial={"email": request.user.email} if i == 0 else {})
            for i in range(num_passengers)
        ]

    base_total = float(flight.price) + (float(return_flight.price) if return_flight else 0)

    return render(request, "flights/book_step1.html", {
        "flight": flight,
        "return_flight": return_flight,
        "passenger_forms": forms,
        "num_passengers": num_passengers,
        "total_price": base_total,
    })


@login_required
def book_step2(request, flight_id):
    bs = BookingSession(request)
    if not bs.get_passengers():
        messages.warning(request, "Vaša sesija je istekla. Molimo počnite rezervaciju iznova.")
        return redirect("home")

    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(bs)

    if request.method == "POST":
        seat_class = request.POST.get("seat_class")
        bs.set_seat_class(seat_class)

        dep_price = flight.price + SEAT_PRICES.get(seat_class, 0)
        ret_price = return_flight.price + SEAT_PRICES.get(seat_class, 0) if return_flight else 0
        bs.set_total_price(float(dep_price + ret_price))

        return redirect("book_step3", flight_id=flight.id)

    seat_options = [{"name": k, "price": v} for k, v in SEAT_PRICES.items()]
    base_total = float(flight.price) + (float(return_flight.price) if return_flight else 0)

    return render(request, "flights/book_step2.html", {
        "flight": flight,
        "return_flight": return_flight,
        "seat_options": seat_options,
        "total_price": base_total,
    })


@login_required
def book_step3(request, flight_id):
    bs = BookingSession(request)
    if not bs.get_passengers() or not bs.get_seat_class():
        messages.warning(request, "Vaša sesija je istekla. Molimo počnite rezervaciju iznova.")
        return redirect("home")

    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(bs)

    num_passengers = bs.get_num_passengers()
    all_selected = bs.get_selected_seats()
    selected = all_selected.get(str(flight_id), [])

    taken = set(
        Ticket.objects.filter(flight=flight)
        .values_list("seat_number", flat=True)
    )

    if request.method == "POST":
        try:
            picks = json.loads(request.POST.get("selected_seats_json", "[]"))
        except (json.JSONDecodeError, ValueError):
            picks = []

        picks = [p for p in picks if isinstance(p, str) and p not in taken]
        all_selected[str(flight_id)] = picks
        bs.set_selected_seats(all_selected)
        selected = picks

        if len(selected) >= num_passengers:
            if return_flight and str(return_flight.id) not in all_selected:
                return redirect("book_step3", flight_id=return_flight.id)
            outbound_id = bs.get_outbound_flight_id() or flight.id
            return redirect("book_step4", flight_id=outbound_id)

    seat_positions = build_seat_positions(
        total_seats=flight.total_seats,
        taken_seats=set(map(str, taken)),
        selected_seats=set(),
        seats_per_row=6,
    )

    return render(request, "flights/book_step3.html", {
        "flight": flight,
        "return_flight": return_flight,
        "seat_positions": seat_positions,
        "selected_seats": selected,
        "num_passengers": num_passengers,
        "remaining": num_passengers - len(selected),
        "total_price": bs.get_total_price() or float(flight.price),
    })


@login_required
def book_step4(request, flight_id):
    bs = BookingSession(request)
    if not bs.get_passengers() or not bs.get_seat_class() or not bs.get_selected_seats():
        messages.warning(request, "Vaša sesija je istekla. Molimo počnite rezervaciju iznova.")
        return redirect("home")

    flight = get_object_or_404(Flight, id=flight_id)
    total = bs.init_price(float(flight.price))

    if request.method == "POST":
        lug = request.POST.get("luggage_option")
        eq = request.POST.get("equipment_option")
        extra = LUGGAGE.get(lug, 0) + EQUIPMENT.get(eq, 0)
        bs.set_luggage(lug)
        bs.set_equipment(eq)
        bs.set_total_price(total + extra)

        return redirect("book_step5", flight_id=flight.id)

    return render(request, "flights/book_step4.html", {
        "flight": flight,
        "total_price": total,
        "luggage_options": LUGGAGE,
        "equipment_options": EQUIPMENT,
    })


@login_required
def book_step5(request, flight_id):
    bs = BookingSession(request)
    if not bs.get_passengers() or not bs.get_seat_class() or not bs.get_selected_seats():
        messages.warning(request, "Vaša sesija je istekla. Molimo počnite rezervaciju iznova.")
        return redirect("home")

    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(bs)
    passengers = bs.get_passengers()
    seat_class = bs.get_seat_class()
    all_selected = bs.get_selected_seats()
    luggage = bs.get_luggage()
    equipment = bs.get_equipment()
    total_price = bs.init_price(float(flight.price))

    if request.method == "GET":
        currency = request.session.get('currency', 'EUR')
        rate = get_rates().get(currency, 1.0)
        converted_total = round(float(total_price) * rate, 2)
        return render(request, "flights/book_step5.html", {
            "flight": flight,
            "return_flight": return_flight,
            "total_price": total_price,
            "PAYPAL_CLIENT_ID": getattr(settings, "PAYPAL_CLIENT_ID", ""),
            "paypal_currency": currency,
            "paypal_amount": f"{converted_total:.2f}",
        })

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"status": "error", "msg": "Invalid JSON"})

    order_id = payload.get("orderID")
    if order_id:
        try:
            capture = capture_paypal_order(order_id)
            if capture.get("status") != "COMPLETED":
                return JsonResponse({"status": "error", "msg": "Payment not completed by PayPal."})
        except Exception as e:
            return JsonResponse({"status": "error", "msg": f"PayPal capture failed: {e}"})

    result = process_booking(
        user=request.user,
        flight=flight,
        return_flight=return_flight,
        passengers=passengers,
        seat_class=seat_class,
        all_selected_seats=all_selected,
        total_price=total_price,
        luggage=luggage,
        equipment=equipment,
        currency=request.session.get('currency', 'EUR'),
    )

    if result["status"] == "ok":
        bs.clear()
    return JsonResponse(result)


@login_required
def book_success(request):
    tickets = Ticket.objects.filter(purchased_by=request.user).order_by("-id")[:10]
    return render(request, "flights/book_success.html", {"tickets": tickets})
