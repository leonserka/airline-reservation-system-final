from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

_started = False


def send_reminders():
    from django.utils import timezone
    from .models import Flight, Ticket
    from .services.email_service import send_flight_reminder_email

    now = timezone.now()
    today = date.today()

    candidates = Flight.objects.filter(
        notification_sent=False,
        date__gte=today,
        date__lte=today + timedelta(days=2),
    )

    for flight in candidates:
        time_until = flight.departure_datetime - now
        if timedelta(hours=23) <= time_until <= timedelta(hours=25):
            tickets = Ticket.objects.filter(flight=flight, status=Ticket.STATUS_BOOKED)
            for ticket in tickets:
                send_flight_reminder_email(ticket.email, ticket.passenger_name, flight)
                print(f"[SCHEDULER] Sent 24h reminder to {ticket.email} for flight {flight.flight_number}")
            flight.notification_sent = True
            flight.save(update_fields=["notification_sent"])


def start():
    global _started
    if _started:
        return
    _started = True
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, "interval", minutes=5, id="flight_reminders")
    scheduler.start()
    print("[SCHEDULER] Flight reminder scheduler started.")
