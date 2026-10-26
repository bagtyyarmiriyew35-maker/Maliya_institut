import ipaddress
from django.conf import settings
from django.shortcuts import render
from .models import VisitorLog, SiteSettings, AllowedIP
from .audit import get_client_ip, parse_user_agent, log_admin_action


class DynamicHtmlNoCacheMiddleware:
    """
    Ensures dynamic HTML pages are not stored in browser or Nginx heuristic cache
    so language changes, login states, and dynamic content update instantly
    without requiring manual browser refreshes (F5).
    Also synchronizes ?lang= query parameter into session and site_lang cookie.
    Static and media assets are unaffected and remain cached by Nginx.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        target_lang = None
        get_lang = request.GET.get('lang')
        if get_lang:
            candidate = str(get_lang).strip().lower()
            if candidate in ['eng', 'en']:
                target_lang = 'eng'
            elif candidate in ['rus', 'ru']:
                target_lang = 'rus'
            else:
                target_lang = 'tm'
            request.session['lang'] = target_lang
            request.session.modified = True

        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Vary'] = 'Cookie'
            if target_lang:
                response.set_cookie('site_lang', target_lang, max_age=365 * 24 * 60 * 60, path='/', samesite='Lax')
        return response


class VisitorTrackingMiddleware:
    """
    Tracks page views and visitor activity across the site.
    Safely captures path, visitor IP, device, browser, referer and language.
    Filters out static assets, media, bot health checks, and API calls.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only log successful GET requests serving HTML
        if request.method == 'GET' and response.status_code == 200:
            content_type = response.get('Content-Type', '')
            if 'text/html' in content_type:
                path = request.path
                # Skip asset paths and internal endpoints
                if not path.startswith(('/static/', '/media/', '/favicon', '/tinymce/', '/api/')):
                    self.record_visit(request, path)

        return response

    def record_visit(self, request, path):
        try:
            ip = get_client_ip(request)
            raw_ua = request.META.get('HTTP_USER_AGENT', '')
            device = parse_user_agent(raw_ua)
            referer = (request.META.get('HTTP_REFERER') or '')[:500]
            lang = request.session.get('lang') or request.GET.get('lang') or 'tm'

            is_auth = False
            user_name = ''
            if hasattr(request, 'user') and request.user.is_authenticated:
                is_auth = True
                user_name = request.user.username

            # Compute human-readable page name
            if path == '/' or path == '':
                page_title = 'Baş sahypa'
            elif path.startswith('/news/'):
                page_title = 'Täzelikler'
            elif path.startswith('/contact/'):
                page_title = 'Habarlaşmak'
            elif path.startswith('/faculty/'):
                page_title = 'Fakultet sahypasy'
            elif path.startswith('/department/'):
                page_title = 'Kafedra sahypasy'
            elif path.startswith('/p/'):
                slug = path.strip('/').split('/')[-1]
                page_title = f"Sahypa ({slug})"
            elif path.startswith('/library/'):
                page_title = 'Kitaphana / Neşirler'
            elif path.startswith('/panel/'):
                page_title = 'Admin Panel'
            else:
                page_title = path[:50]

            VisitorLog.objects.create(
                path=path[:500],
                page_title=page_title,
                ip_address=ip,
                user_agent=raw_ua,
                device=device,
                referer=referer,
                lang=lang,
                is_authenticated=is_auth,
                user_name=user_name,
            )
        except Exception:
            pass


class AdminIPRestrictionMiddleware:
    """
    Restricts access to administrative endpoints (/panel/ and /admin/)
    to explicitly allowed IP addresses configured by the administrator.
    If IP restriction is disabled, all IPs are permitted.
    If enabled but no active allowed IPs are in the database, allows requests
    as a safety fallback to prevent accidental admin lockout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Only intercept administrative paths
        if path.startswith('/panel/') or path.startswith('/admin/'):
            try:
                settings_obj = SiteSettings.get_settings()
                if settings_obj and getattr(settings_obj, 'ip_restriction_enabled', False):
                    client_ip = get_client_ip(request)
                    if not self.is_ip_allowed(client_ip):
                        # Safely record unauthorized intrusion attempt in audit log
                        log_admin_action(
                            request,
                            'VIEW',
                            'Howpsuzlyk',
                            object_repr=client_ip,
                            details=f"Rugsat berilmedik IP-den admin paneline giriş synanyşygy petiklendi: {client_ip} ({path})"
                        )
                        # Return 403 Access Denied template
                        return render(
                            request,
                            'panel/403_ip_blocked.html',
                            {
                                'client_ip': client_ip,
                                'blocked_path': path,
                            },
                            status=403
                        )
            except Exception:
                # Never crash the application on middleware inspection errors
                pass

        return self.get_response(request)

    @staticmethod
    def is_ip_allowed(client_ip):
        """
        Validates client_ip against hardcoded safe IPs (ADMIN_ALWAYS_ALLOWED_IPS in settings.py)
        and active AllowedIP records in the database.
        Supports single IPv4/IPv6, CIDR notation (e.g. 192.168.1.0/24), and exact strings.
        """
        client_ip = (client_ip or '').strip()
        if not client_ip:
            return False

        # 1. Check hardcoded safe IPs directly from settings.py (Guaranteed access in code)
        hardcoded_safe_ips = list(getattr(settings, 'ADMIN_ALWAYS_ALLOWED_IPS', [
            '127.0.0.1', '::1', '95.85.109.26', '95.85.108.94', '95.85.108.0/22', '20.20.21.143', '216.250.9.135', '216.250.10.252'
        ]))
        if client_ip in hardcoded_safe_ips:
            return True

        # 2. Database AllowedIP active records
        active_ips = list(AllowedIP.objects.filter(is_active=True).values_list('ip_address', flat=True))
        all_whitelist = hardcoded_safe_ips + active_ips

        # Parse client IP
        try:
            client_addr = ipaddress.ip_address(client_ip)
        except ValueError:
            return client_ip in all_whitelist

        for raw in all_whitelist:
            raw = (raw or '').strip()
            if not raw:
                continue
            try:
                if '/' in raw:
                    net = ipaddress.ip_network(raw, strict=False)
                    if client_addr in net:
                        return True
                else:
                    addr = ipaddress.ip_address(raw)
                    if client_addr == addr:
                        return True
            except ValueError:
                if raw == client_ip:
                    return True

        return False

