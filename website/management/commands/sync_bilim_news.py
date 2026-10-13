import sys
from django.core.management.base import BaseCommand
from website.bilim_scraper import sync_bilim_news

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


class Command(BaseCommand):
    help = "Bilim.tm sahypasyndan iň soňky 9 habary çekip bazany täzeleýär."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=9,
            help='Sany (default: 9)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        self.stdout.write(f"Bilim.tm: {limit} sany habar cekilyar...")
        res = sync_bilim_news(limit=limit)
        if res.get('success'):
            msg = res.get('message', '').encode('ascii', errors='replace').decode('ascii')
            self.stdout.write(self.style.SUCCESS(f"Success: {msg}"))
        else:
            msg = res.get('message', '').encode('ascii', errors='replace').decode('ascii')
            self.stdout.write(self.style.ERROR(f"Error: {msg}"))
