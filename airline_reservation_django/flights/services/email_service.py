from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_receipt_email(to_email, total_sum, pdf_buffer=None, flight=None, user=None):
    try:
        subject = f"Booking Confirmed: {flight.departure_city} → {flight.arrival_city} on {flight.date}" if flight else "Booking Confirmation"
        username = user.username if user else "Passenger"
        route = f"{flight.departure_city} → {flight.arrival_city}" if flight else "N/A"
        date = str(flight.date) if flight else "N/A"

        text_body = (
            f"Dear {username},\n\nYour booking is confirmed!\n\n"
            f"Route: {route}\nDate: {date}\nTotal paid: €{total_sum:.2f}\n\n"
            f"Thank you for booking with Airline Reservation.\n"
        )

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;border:1px solid #e0e3e8;border-radius:8px;overflow:hidden;">
          <div style="background:#003366;padding:24px;text-align:center;">
            <h2 style="color:#fff;margin:0;font-size:20px;">Booking Confirmed ✓</h2>
          </div>
          <div style="padding:28px 32px;">
            <p style="font-size:16px;color:#222;">Dear <strong>{username}</strong>,</p>
            <p style="color:#444;">Your flight has been successfully booked.</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;">
              <tr><td style="padding:8px 0;color:#888;font-size:13px;">Route</td><td style="padding:8px 0;font-weight:600;color:#003366;">{route}</td></tr>
              <tr><td style="padding:8px 0;color:#888;font-size:13px;">Date</td><td style="padding:8px 0;font-weight:600;">{date}</td></tr>
              <tr><td style="padding:8px 0;color:#888;font-size:13px;">Amount paid</td><td style="padding:8px 0;font-weight:600;color:#1a8754;">€{total_sum:.2f}</td></tr>
            </table>
            <p style="font-size:13px;color:#888;margin-top:24px;">If a PDF receipt is attached, please save it for your records.</p>
          </div>
          <div style="background:#f0f2f5;padding:14px;text-align:center;font-size:12px;color:#aaa;">
            Airline Reservation System &copy; 2026
          </div>
        </div>
        """

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@airline.com')
        msg = EmailMultiAlternatives(subject=subject, body=text_body, from_email=from_email, to=[to_email])
        msg.attach_alternative(html_body, "text/html")
        if pdf_buffer:
            msg.attach("receipt.pdf", pdf_buffer.getvalue(), "application/pdf")
        msg.send()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send receipt email to {to_email}: {e}")
        return False
