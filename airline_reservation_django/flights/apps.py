import sys
from django.apps import AppConfig

_SKIP_COMMANDS = {'migrate', 'makemigrations', 'test', 'collectstatic', 'shell', 'createsuperuser', 'seed_routes'}


class FlightsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flights'

    def ready(self):
        if set(sys.argv) & _SKIP_COMMANDS:
            return
        try:
            from . import scheduler
            scheduler.start()
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")
