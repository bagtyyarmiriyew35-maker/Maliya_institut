"""
URL configuration for maliya_project project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

def serve_media_files(request, path):
    response = serve(request, path, document_root=settings.MEDIA_ROOT)
    if path.lower().endswith('.pdf'):
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = 'inline'
    elif path.lower().endswith('.mp4'):
        response['Content-Type'] = 'video/mp4'
    elif path.lower().endswith('.webm'):
        response['Content-Type'] = 'video/webm'
    elif path.lower().endswith('.webp'):
        response['Content-Type'] = 'image/webp'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

import os
from django.http import FileResponse, HttpResponse

def serve_favicon(request):
    favicon_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'favicon.ico')
    if os.path.exists(favicon_path):
        return FileResponse(open(favicon_path, 'rb'), content_type='image/x-icon')
    loga_path = os.path.join(settings.BASE_DIR, 'media', 'loga.png')
    if os.path.exists(loga_path):
        return FileResponse(open(loga_path, 'rb'), content_type='image/png')
    return HttpResponse(status=404)

def serve_robots_txt(request):
    content = "User-agent: *\nAllow: /\nDisallow: /panel/\nDisallow: /admin/\n"
    return HttpResponse(content, content_type='text/plain')

from website.views import serve_pdf_engine_lib, serve_pdf_engine_worker

urlpatterns = [
    path('favicon.ico', serve_favicon, name='favicon'),
    path('robots.txt', serve_robots_txt, name='robots_txt'),
    path('admin/', admin.site.urls),          # Django's built-in admin (kept)
    path('tinymce/', include('tinymce.urls')),  # TinyMCE JS serving
    path('panel/', include('website.panel_urls')),  # Custom Admin Panel
    path('pdfengine/lib.js', serve_pdf_engine_lib, name='serve_pdf_lib'),
    path('pdfengine/worker.js', serve_pdf_engine_worker, name='serve_pdf_worker'),
    re_path(r'^media/(?P<path>.*)$', serve_media_files),
    path('', include('website.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
