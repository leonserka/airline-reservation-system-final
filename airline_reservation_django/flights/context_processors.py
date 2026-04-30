from .services.currency_service import CURRENCIES


def currency_context(request):
    selected = request.session.get('currency', 'EUR')
    if selected not in CURRENCIES:
        selected = 'EUR'
    return {
        'selected_currency': selected,
        'currency_choices': list(CURRENCIES.keys()),
    }
