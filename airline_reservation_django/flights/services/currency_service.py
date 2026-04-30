import time
import requests as http_requests

CURRENCIES = {
    'EUR': '€',
    'USD': '$',
    'CHF': 'CHF',
    'GBP': '£',
    'HUF': 'Ft',
    'CZK': 'Kč',
}

_cache = {'rates': {'EUR': 1.0}, 'ts': 0.0}
_CACHE_TTL = 3600


def get_rates():
    now = time.time()
    if now - _cache['ts'] < _CACHE_TTL:
        return _cache['rates']
    try:
        targets = ','.join(c for c in CURRENCIES if c != 'EUR')
        resp = http_requests.get(
            'https://api.frankfurter.app/latest',
            params={'from': 'EUR', 'to': targets},
            timeout=5,
        )
        data = resp.json()
        rates = {'EUR': 1.0}
        rates.update(data.get('rates', {}))
        _cache['rates'] = rates
        _cache['ts'] = now
    except Exception:
        pass
    return _cache['rates']


def format_price(amount, currency):
    rates = get_rates()
    rate = rates.get(currency, 1.0)
    converted = float(amount) * rate
    symbol = CURRENCIES.get(currency, currency)
    if currency in ('HUF', 'CZK'):
        return f"{converted:,.0f} {symbol}"
    if currency == 'CHF':
        return f"{symbol} {converted:,.2f}"
    return f"{symbol}{converted:,.2f}"
