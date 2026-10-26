import os
import io
import json
import zipfile
import sys
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone


def safe_msg(text):
    """Encodes non-ASCII characters gracefully for Windows CP1251/CP866 console output."""
    encoding = sys.stdout.encoding or 'utf-8'
    return str(text).encode(encoding, errors='replace').decode(encoding)


class Command(BaseCommand):
    help = "Saytyn ahli maglumatlaryny (JSON) we media fayllaryny atiyaclyk arhiw edip yazdyryar"

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['full', 'json', 'media'],
            default='full',
            help='Atiyaclyk gornusi: full (JSON + Media), json (dine maglumatlar), media (dine media bukjasy)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='',
            help='Arhiwin yazdyryljak yeri (default: saytyn backups/ bukjasy)'
        )

    def handle(self, *args, **options):
        backup_type = options['type']
        output_dir = options['output_dir'] or os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(output_dir, exist_ok=True)

        now_str = timezone.now().strftime('%Y-%m-%d_%H%M%S')
        self.stdout.write(safe_msg(f">>> Atiyaclyk doretmek baslandy (Gornusi: {backup_type}) ..."))

        if backup_type == 'json':
            filename = f"tdmai_maglumatlar_{now_str}.json"
            target_path = os.path.join(output_dir, filename)
            buf = io.StringIO()
            call_command(
                'dumpdata', 'website',
                stdout=buf,
                indent=2,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True
            )
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(buf.getvalue())

            size_kb = os.path.getsize(target_path) / 1024
            self.stdout.write(safe_msg(f">>> Ustunlikli doredildi: {filename} ({size_kb:.1f} KB)"))
            self.stdout.write(safe_msg(f"    Bukja: {output_dir}"))
            return

        # Full or Media Zip
        filename = f"tdmai_{'doly_atiyaclyk' if backup_type == 'full' else 'media'}_{now_str}.zip"
        target_path = os.path.join(output_dir, filename)
        media_root = str(settings.MEDIA_ROOT)

        with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if backup_type == 'full':
                self.stdout.write(safe_msg(" -> Maglumatlar binyady (JSON) arhiwe gosulyar..."))
                buf = io.StringIO()
                call_command(
                    'dumpdata', 'website',
                    stdout=buf,
                    indent=2,
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True
                )
                zf.writestr('database_backup.json', buf.getvalue().encode('utf-8'))

                manifest = {
                    'project': 'Türkmen Döwlet Maliýe Instituty (tdmai.edu.tm)',
                    'export_date': now_str,
                    'backup_type': 'full',
                }
                zf.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))

            self.stdout.write(safe_msg(" -> Media bukjasy arhiwe gosulyar..."))
            file_count = 0
            if os.path.exists(media_root):
                for root, dirs, files in os.walk(media_root):
                    for f in files:
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, media_root)
                        zip_entry = os.path.join('media', rel_p).replace('\\', '/')
                        try:
                            zf.write(full_p, zip_entry)
                            file_count += 1
                        except (OSError, FileNotFoundError):
                            pass

        size_mb = os.path.getsize(target_path) / (1024 * 1024)
        self.stdout.write(safe_msg(
            f">>> Atiyaclyk arhiwi tayyar boldy! ({file_count} media fayl, {size_mb:.2f} MB)\n"
            f"    Faýl: {filename}\n"
            f"    Bukja: {output_dir}"
        ))
