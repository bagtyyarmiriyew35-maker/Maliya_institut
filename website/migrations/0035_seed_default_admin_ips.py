from django.db import migrations


def seed_default_ips(apps, schema_editor):
    AllowedIP = apps.get_model('website', 'AllowedIP')
    default_ips = [
        ('20.20.21.143', 'Esasy Administrator (Siziň Kompýuteriňiz)'),
        ('127.0.0.1', 'Lokal Serwer (Localhost)'),
        ('216.250.9.135', 'Institut Serweri (Public IP 1)'),
        ('216.250.10.252', 'Institut Serweri (Public IP 2)'),
    ]
    for ip, label in default_ips:
        if not AllowedIP.objects.filter(ip_address=ip).exists():
            AllowedIP.objects.create(ip_address=ip, label=label, is_active=True)


def remove_default_ips(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0034_allowedip_sitesettings_ip_restriction_enabled'),
    ]

    operations = [
        migrations.RunPython(seed_default_ips, reverse_code=remove_default_ips),
    ]
