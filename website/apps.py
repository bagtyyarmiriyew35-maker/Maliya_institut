import os
import sys
import threading
import time
from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    name = 'website'

    def ready(self):
        import website.signals
        
        # Migrasiýa ýa-da başga dolandyryş buýruklarynda arka planda thread açmazlyk üçin
        commands_to_skip = {'makemigrations', 'migrate', 'collectstatic', 'check', 'test', 'shell'}
        if any(cmd in sys.argv for cmd in commands_to_skip):
            return

        # Runserver wagtynda diňe esasy prosesde (RUN_MAIN == 'true') işleýär
        is_runserver = 'runserver' in sys.argv
        if is_runserver and os.environ.get('RUN_MAIN') != 'true':
            return

        # Eger ýörite ýapylmadyk bolsa (DISABLE_BACKGROUND_SCRAPER == 'True'), ähli ýerde awtomatiki işleýär
        if os.environ.get('DISABLE_BACKGROUND_SCRAPER') == 'True':
            return

        def run_hourly_sync():
            # Serwer doly işe girýänçä 10 sekunt garaşýar
            time.sleep(10)
            while True:
                try:
                    from website.bilim_scraper import sync_bilim_news
                    sync_bilim_news(limit=9)
                except Exception:
                    pass
                # Her 1 sagatdan (3600 sekunt) täzeden barlaýar
                time.sleep(3600)

        sync_thread = threading.Thread(
            target=run_hourly_sync,
            daemon=True,
            name="BilimNewsHourlySyncThread"
        )
        sync_thread.start()
