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

