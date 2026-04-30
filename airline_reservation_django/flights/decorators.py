from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .services.booking_session import BookingSession


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_booking_session(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not BookingSession(request).get_passengers():
            messages.warning(request, "Vaša sesija je istekla. Molimo počnite rezervaciju iznova.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper
