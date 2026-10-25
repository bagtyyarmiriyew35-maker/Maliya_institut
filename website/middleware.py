from .models import VisitorLog
from .audit import get_client_ip, parse_user_agent


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
