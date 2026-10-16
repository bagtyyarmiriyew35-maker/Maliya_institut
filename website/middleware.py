class DynamicHtmlNoCacheMiddleware:
    """
    Ensures dynamic HTML pages are not stored in browser heuristic cache
    so language changes, login states, and dynamic content update instantly
    without requiring manual browser refreshes (F5).
    Static and media assets are unaffected and remain cached by Nginx.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Vary'] = 'Cookie'
        return response
