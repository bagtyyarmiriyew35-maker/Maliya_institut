import os
import sys
import threading
import time
from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    name = 'website'

    def ready(self):
        import website.signals
        
        # Arka plandaky thread diňe aýratyn buýruk bilen işletmek üçin (Gunicorn işgärlerini dondurmazlygy üçin)
        if os.environ.get('ENABLE_BACKGROUND_SCRAPER') != 'True':
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
