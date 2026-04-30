from django import template
from ..services.currency_service import format_price

register = template.Library()


@register.filter
def currency(amount, selected_currency='EUR'):
    if amount is None or amount == '':
        return ''
    try:
        return format_price(float(amount), str(selected_currency))
    except (ValueError, TypeError):
        return amount
