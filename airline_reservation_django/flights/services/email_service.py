from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.conf import settings
from .currency_service import format_price


_C = {
    'navy':    '#0E1B3A',
    'accent':  '#D05A35',
    'success': '#286B4E',
    'danger':  '#B82F1C',
    'cream':   '#F4EFE6',
    'warm':    '#FAF7F2',
    'white':   '#FFFFFF',
    'text':    '#1C1C1C',
    'muted':   '#7C7168',
    'border':  '#E4DAD0',
}

FONT = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"


def _wrap(header_html, body_html, accent_color=None):
    accent = accent_color or _C['accent']
    return f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{_C['cream']};font-family:{SANS};">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{_C['cream']};padding:32px 16px;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

      <tr><td style="height:4px;background:{accent};border-radius:4px 4px 0 0;font-size:0;">&nbsp;</td></tr>

      <tr><td style="background:{_C['navy']};padding:32px 40px;text-align:center;border-radius:0;">
        <p style="margin:0 0 6px;color:rgba(255,255,255,0.45);font-size:10px;letter-spacing:0.14em;text-transform:uppercase;font-family:{SANS};">Airline Reservation</p>
        {header_html}
      </td></tr>

      <tr><td style="background:{_C['white']};padding:36px 40px;">
        {body_html}
      </td></tr>

      <tr><td style="background:{_C['warm']};padding:20px 40px;text-align:center;border-top:1px solid {_C['border']};border-radius:0 0 4px 4px;">
        <p style="margin:0;font-size:12px;color:{_C['muted']};font-family:{SANS};">
          &copy; 2026 Airline Reservation System &nbsp;·&nbsp; All rights reserved
        </p>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


def _row(label, value, value_color=None):
    color = value_color or _C['text']
    return f"""
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid {_C['border']};font-size:13px;color:{_C['muted']};font-family:{SANS};width:40%;">{label}</td>
        <td style="padding:10px 0;border-bottom:1px solid {_C['border']};font-size:14px;font-weight:600;color:{color};font-family:{SANS};">{value}</td>
      </tr>"""


def send_receipt_email(to_email, total_sum, pdf_buffer=None, flight=None, user=None, currency='EUR'):
    try:
        subject = (
            f"Booking Confirmed: {flight.departure_city} → {flight.arrival_city} on {flight.date}"
            if flight else "Booking Confirmation"
        )
        username = user.username if user else "Passenger"
        route = f"{flight.departure_city} → {flight.arrival_city}" if flight else "N/A"
        date = str(flight.date) if flight else "N/A"
        price_display = format_price(total_sum, currency)

        text_body = (
            f"Dear {username},\n\nYour booking is confirmed!\n\n"
            f"Route: {route}\nDate: {date}\nTotal paid: {price_display}\n\n"
            f"Thank you for booking with Airline Reservation.\n"
        )

        header_html = f"""
          <h1 style="margin:8px 0 0;color:{_C['white']};font-family:{FONT};font-size:26px;font-weight:600;font-style:italic;letter-spacing:-0.3px;">
            Booking Confirmed
          </h1>
          <p style="margin:10px 0 0;color:rgba(255,255,255,0.55);font-size:13px;font-family:{SANS};">Your seat is reserved. Safe travels!</p>"""

        body_html = f"""
          <p style="margin:0 0 6px;font-size:16px;color:{_C['text']};font-family:{SANS};">Dear <strong>{username}</strong>,</p>
          <p style="margin:0 0 28px;font-size:14px;color:{_C['muted']};font-family:{SANS};line-height:1.6;">
            Your flight has been successfully booked and payment received. A PDF receipt is attached to this email.
          </p>

          <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
            <tr><td style="background:{_C['cream']};border:1px solid {_C['border']};border-radius:10px;padding:20px 24px;">
              <p style="margin:0 0 4px;font-size:11px;font-family:{SANS};color:{_C['muted']};text-transform:uppercase;letter-spacing:0.1em;">Route</p>
              <p style="margin:0;font-family:{FONT};font-size:22px;font-weight:600;color:{_C['navy']};font-style:italic;">{route}</p>
            </td></tr>
          </table>

          <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
            {_row('Date', date)}
            {_row('Amount paid', price_display, _C['success'])}
          </table>

          <p style="margin:0;font-size:13px;color:{_C['muted']};font-family:{SANS};line-height:1.6;border-left:3px solid {_C['accent']};padding-left:14px;">
            If you have any questions about your booking, please contact our support team.
          </p>"""

        html_body = _wrap(header_html, body_html)

        msg = EmailMultiAlternatives(subject=subject, body=text_body,
                                     from_email=settings.EMAIL_HOST_USER, to=[to_email])
        msg.attach_alternative(html_body, "text/html")
        if pdf_buffer:
            msg.attach("receipt.pdf", pdf_buffer.getvalue(), "application/pdf")
        msg.send()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send receipt email to {to_email}: {e}")
        return False


def send_password_changed_email(to_email, username):
    try:
        subject = "Your password was changed"
        text_body = (
            f"Hi {username},\n\n"
            f"Your Airline Reservation account password was just changed.\n"
            f"If you did not do this, please contact support immediately.\n\n"
            f"Airline Reservation System"
        )

        header_html = f"""
          <h1 style="margin:8px 0 0;color:{_C['white']};font-family:{FONT};font-size:24px;font-weight:600;font-style:italic;">
            Password Changed
          </h1>"""

        body_html = f"""
          <p style="margin:0 0 6px;font-size:16px;color:{_C['text']};font-family:{SANS};">Hi <strong>{username}</strong>,</p>
          <p style="margin:0 0 24px;font-size:14px;color:{_C['muted']};font-family:{SANS};line-height:1.6;">
            Your account password was successfully updated.
          </p>
          <table cellpadding="0" cellspacing="0" width="100%">
            <tr><td style="background:#FEF3E0;border:1px solid #E8A82A;border-radius:8px;padding:16px 20px;">
              <p style="margin:0;font-size:14px;color:#7A4F0A;font-family:{SANS};line-height:1.6;">
                <strong>Not you?</strong> If you did not make this change, please contact our support team immediately to secure your account.
              </p>
            </td></tr>
          </table>"""

        html_body = _wrap(header_html, body_html, _C['navy'])

        msg = EmailMultiAlternatives(subject=subject, body=text_body,
                                     from_email=settings.EMAIL_HOST_USER, to=[to_email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send password changed email to {to_email}: {e}")
        return False


def send_flight_canceled_email(to_email, passenger_name, flight):
    try:
        flight_number = flight.flight_number
        route = f"{flight.departure_city} → {flight.arrival_city}"
        flight_date = str(flight.date)

        subject = f"Flight {flight_number} Canceled"
        text_body = (
            f"Dear {passenger_name},\n\n"
            f"We regret to inform you that flight {flight_number} ({route}) on {flight_date} has been canceled.\n"
            f"Your refund will be available within the next 24 hours. We apologize for the inconvenience.\n\n"
            f"Airline Reservation System"
        )

        header_html = f"""
          <h1 style="margin:8px 0 0;color:{_C['white']};font-family:{FONT};font-size:24px;font-weight:600;font-style:italic;">
            Flight Canceled
          </h1>
          <p style="margin:10px 0 0;color:rgba(255,255,255,0.55);font-size:13px;font-family:{SANS};">We apologize for the inconvenience</p>"""

        body_html = f"""
          <p style="margin:0 0 6px;font-size:16px;color:{_C['text']};font-family:{SANS};">Dear <strong>{passenger_name}</strong>,</p>
          <p style="margin:0 0 28px;font-size:14px;color:{_C['muted']};font-family:{SANS};line-height:1.6;">
            We regret to inform you that the following flight has been <strong>canceled</strong>.
          </p>

          <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
            {_row('Flight', flight_number)}
            {_row('Route', route)}
            {_row('Date', flight_date)}
          </table>

          <table cellpadding="0" cellspacing="0" width="100%">
            <tr><td style="background:#FCECEA;border:1px solid {_C['danger']};border-radius:8px;padding:16px 20px;border-left:4px solid {_C['danger']};">
              <p style="margin:0;font-size:14px;color:#7A1A14;font-family:{SANS};line-height:1.6;">
                Your refund will be processed within <strong>24 hours</strong>. We sincerely apologize for any inconvenience caused.
              </p>
            </td></tr>
          </table>"""

        html_body = _wrap(header_html, body_html, _C['danger'])

        msg = EmailMultiAlternatives(subject=subject, body=text_body,
                                     from_email=settings.EMAIL_HOST_USER, to=[to_email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send flight canceled email to {to_email}: {e}")
        return False


def send_ticket_canceled_email(to_email, passenger_name, flight, ticket):
    try:
        flight_number = flight.flight_number
        route = f"{flight.departure_city} → {flight.arrival_city}"
        flight_date = str(flight.date)
        seat_class = ticket.seat_class

        subject = f"Ticket Canceled – {flight_number} ({route})"
        text_body = (
            f"Dear {passenger_name},\n\n"
            f"Your {seat_class} class ticket for flight {flight_number} ({route}) on {flight_date} has been successfully canceled.\n"
            f"Your payment has been marked as refunded. Thank you for flying with us.\n\n"
            f"Airline Reservation System"
        )

        header_html = f"""
          <h1 style="margin:8px 0 0;color:{_C['white']};font-family:{FONT};font-size:24px;font-weight:600;font-style:italic;">
            Ticket Canceled
          </h1>
          <p style="margin:10px 0 0;color:rgba(255,255,255,0.55);font-size:13px;font-family:{SANS};">Your refund has been confirmed</p>"""

        body_html = f"""
          <p style="margin:0 0 6px;font-size:16px;color:{_C['text']};font-family:{SANS};">Dear <strong>{passenger_name}</strong>,</p>
          <p style="margin:0 0 28px;font-size:14px;color:{_C['muted']};font-family:{SANS};line-height:1.6;">
            Your ticket has been successfully <strong>canceled</strong> and your payment <strong>refunded</strong>.
          </p>

          <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
            {_row('Flight', flight_number)}
            {_row('Route', route)}
            {_row('Date', flight_date)}
            {_row('Class', seat_class)}
          </table>

          <table cellpadding="0" cellspacing="0" width="100%">
            <tr><td style="background:#E7F4EE;border:1px solid {_C['success']};border-radius:8px;padding:16px 20px;border-left:4px solid {_C['success']};">
              <p style="margin:0;font-size:14px;color:#1A5C38;font-family:{SANS};line-height:1.6;">
                Your refund has been confirmed. Thank you for flying with us — we hope to see you again soon.
              </p>
            </td></tr>
          </table>"""

        html_body = _wrap(header_html, body_html, _C['danger'])

        msg = EmailMultiAlternatives(subject=subject, body=text_body,
                                     from_email=settings.EMAIL_HOST_USER, to=[to_email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send ticket canceled email to {to_email}: {e}")
        return False


def send_flight_reminder_email(to_email, passenger_name, flight):
    try:
        flight_number = flight.flight_number
        route = f"{flight.departure_city} → {flight.arrival_city}"
        departure = flight.departure_datetime.strftime("%b %d at %H:%M")

        subject = f"Reminder: Your flight {flight_number} departs in 24 hours"
        text_body = (
            f"Dear {passenger_name},\n\n"
            f"Your flight {flight_number} ({route}) departs in approximately 24 hours ({departure} local time).\n\n"
            f"If you haven't checked in online yet, please do so before departure.\n\n"
            f"Airline Reservation System"
        )

        header_html = f"""
          <h1 style="margin:8px 0 0;color:{_C['white']};font-family:{FONT};font-size:24px;font-weight:600;font-style:italic;">
            Flight in 24 Hours
          </h1>
          <p style="margin:10px 0 0;color:rgba(255,255,255,0.55);font-size:13px;font-family:{SANS};">Time to get ready for your journey</p>"""

        body_html = f"""
          <p style="margin:0 0 6px;font-size:16px;color:{_C['text']};font-family:{SANS};">Dear <strong>{passenger_name}</strong>,</p>
          <p style="margin:0 0 28px;font-size:14px;color:{_C['muted']};font-family:{SANS};line-height:1.6;">
            Your flight departs in approximately <strong>24 hours</strong>. Here are your details:
          </p>

          <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
            <tr><td style="background:{_C['cream']};border:1px solid {_C['border']};border-radius:10px;padding:20px 24px;">
              <p style="margin:0 0 4px;font-size:11px;font-family:{SANS};color:{_C['muted']};text-transform:uppercase;letter-spacing:0.1em;">Route</p>
              <p style="margin:0;font-family:{FONT};font-size:22px;font-weight:600;color:{_C['navy']};font-style:italic;">{route}</p>
            </td></tr>
          </table>

          <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
            {_row('Flight', flight_number)}
            {_row('Departure', departure, _C['accent'])}
          </table>

          <table cellpadding="0" cellspacing="0" width="100%">
            <tr><td style="background:{_C['cream']};border:1px solid {_C['border']};border-radius:8px;padding:16px 20px;border-left:4px solid {_C['accent']};">
              <p style="margin:0;font-size:14px;color:{_C['text']};font-family:{SANS};line-height:1.6;">
                Haven't checked in yet? Online check-in is available up to <strong>24 hours</strong> before departure in <em>My Bookings</em>.
              </p>
            </td></tr>
          </table>"""

        html_body = _wrap(header_html, body_html, _C['accent'])

        msg = EmailMultiAlternatives(subject=subject, body=text_body,
                                     from_email=settings.EMAIL_HOST_USER, to=[to_email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send flight reminder email to {to_email}: {e}")
        return False


def send_checkin_email(to_email, flight_number):
    try:
        subject = f"Check-in Confirmed – Flight {flight_number}"
        text_body = f"You have successfully checked in for flight {flight_number}."

        header_html = f"""
          <h1 style="margin:8px 0 0;color:{_C['white']};font-family:{FONT};font-size:24px;font-weight:600;font-style:italic;">
            Check-in Confirmed
          </h1>"""

        body_html = f"""
          <p style="margin:0 0 24px;font-size:14px;color:{_C['muted']};font-family:{SANS};line-height:1.6;">
            You have successfully checked in for your upcoming flight.
          </p>

          <table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
            {_row('Flight', flight_number, _C['navy'])}
          </table>

          <table cellpadding="0" cellspacing="0" width="100%">
            <tr><td style="background:#E7F4EE;border:1px solid {_C['success']};border-radius:8px;padding:16px 20px;border-left:4px solid {_C['success']};">
              <p style="margin:0;font-size:14px;color:#1A5C38;font-family:{SANS};line-height:1.6;">
                Your boarding pass is available in <strong>My Bookings</strong>. Please arrive at the gate at least 45 minutes before departure.
              </p>
            </td></tr>
          </table>"""

        html_body = _wrap(header_html, body_html, _C['success'])

        msg = EmailMultiAlternatives(subject=subject, body=text_body,
                                     from_email=settings.EMAIL_HOST_USER, to=[to_email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send check-in email to {to_email}: {e}")
        return False
