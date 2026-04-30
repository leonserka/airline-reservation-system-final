from django.shortcuts import redirect
from ..services.currency_service import CURRENCIES


def set_currency(request):
    if request.method == 'POST':
        currency = request.POST.get('currency', 'EUR')
        if currency in CURRENCIES:
            request.session['currency'] = currency
    return redirect(request.META.get('HTTP_REFERER', '/'))
