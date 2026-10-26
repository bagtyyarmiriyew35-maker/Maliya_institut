"""
Custom Admin Panel Views — /panel/
All views require staff login. Django's /admin/ remains untouched.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils.text import slugify
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from datetime import datetime
import os

from .templatetags.website_tags import (
    file_category, file_icon, file_color, file_bg_color, file_category_label
)

from .models import (
    Page, SliderImage, News, Faculty, Department,
    Olympiad, Partner, Document, ContactMessage, SiteSettings,
    LibraryCategory, LibraryBook, BilimNews, VisitorLog, AdminAuditLog,
    AllowedIP
)
from .bilim_scraper import sync_bilim_news
from .audit import log_admin_action, get_client_ip
import ipaddress




def generate_unique_slug(title_tm, current_pk=None):
    char_map = {
        'ä': 'a', 'ž': 'z', 'ň': 'n', 'ö': 'o', 'ş': 's', 'ü': 'u', 'ç': 'c', 'ý': 'y',
        'Ä': 'a', 'Ž': 'z', 'Ň': 'n', 'Ö': 'o', 'Ş': 's', 'Ü': 'u', 'Ç': 'c', 'Ý': 'y',
        'I': 'i', 'İ': 'i', 'ı': 'i'
    }
    cleaned_title = "".join(char_map.get(c, c) for c in title_tm)
    base_slug = slugify(cleaned_title)
    if not base_slug:
        base_slug = "page"
    
    slug = base_slug
    counter = 1
    qs = Page.objects.filter(slug=slug)
    if current_pk:
        qs = qs.exclude(pk=current_pk)
    
    while qs.exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        qs = Page.objects.filter(slug=slug)
        if current_pk:
            qs = qs.exclude(pk=current_pk)
            
    return slug


# ─────────────────────────────────────────────
from django.views.decorators.cache import never_cache

# Decorator helper — require staff login & prevent caching
# ─────────────────────────────────────────────

def panel_login_required(view_func):
    """Redirect to panel login if not authenticated and prevent stale browser caching."""
    @never_cache
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('panel_login')
        response = view_func(request, *args, **kwargs)
        if hasattr(response, '__setitem__'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel_dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            log_admin_action(request, 'LOGIN', 'Ulgam', object_repr=user.username, details="Admin ulgama girdi")
            return redirect('panel_dashboard')
        else:
            error = 'Ulanyjy ady ýa-da açar sözi nädogry!'

    return render(request, 'panel/login.html', {'error': error})


def panel_logout(request):
    if request.user.is_authenticated:
        log_admin_action(request, 'LOGOUT', 'Ulgam', object_repr=request.user.username, details="Admin ulgamdan çykdy")
    logout(request)
    return redirect('panel_login')


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@panel_login_required
def panel_dashboard(request):
    stats = {
        'sliders': SliderImage.objects.count(),
        'news': News.objects.count(),
        'pages': Page.objects.count(),
        'faculties': Faculty.objects.count(),
        'departments': Department.objects.count(),
        'documents': Document.objects.count(),
        'olympiads': Olympiad.objects.count(),
        'partners': Partner.objects.count(),
        'library_categories': LibraryCategory.objects.count(),
        'library_books': LibraryBook.objects.count(),
        'messages': ContactMessage.objects.count(),

        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
    }
    recent_news = News.objects.order_by('-published_date')[:5]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    context = {
        'stats': stats,
        'recent_news': recent_news,
        'recent_messages': recent_messages,
    }
    return render(request, 'panel/dashboard.html', context)


# ─────────────────────────────────────────────
# SLIDERS
# ─────────────────────────────────────────────

@panel_login_required
def panel_sliders(request):
    sliders = SliderImage.objects.order_by('order')
    return render(request, 'panel/sliders.html', {'sliders': sliders})


@panel_login_required
def panel_slider_add(request):
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        if not title_tm:
            messages.error(request, 'Türkmençe at hökmanydyr!')
            return render(request, 'panel/slider_form.html', {'action': 'add'})
        slide = SliderImage(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', ''),
            title_ru=request.POST.get('title_ru', ''),
            subtitle_tm=request.POST.get('subtitle_tm', ''),
            subtitle_en=request.POST.get('subtitle_en', ''),
            subtitle_ru=request.POST.get('subtitle_ru', ''),
            link=request.POST.get('link', ''),
            order=int(request.POST.get('order', 0) or 0),
        )
        if 'image' in request.FILES:
            slide.image = request.FILES['image']
        if 'image_en' in request.FILES:
            slide.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            slide.image_ru = request.FILES['image_ru']
        if 'video' in request.FILES:
            slide.video = request.FILES['video']
        slide.save()
        messages.success(request, 'Slider üstünlikli goşuldy!')
        return redirect('panel_sliders')
    return render(request, 'panel/slider_form.html', {'action': 'add'})


@panel_login_required
def panel_slider_edit(request, pk):
    slide = get_object_or_404(SliderImage, pk=pk)
    if request.method == 'POST':
        slide.title_tm = request.POST.get('title_tm', slide.title_tm).strip()
        slide.title_en = request.POST.get('title_en', '')
        slide.title_ru = request.POST.get('title_ru', '')
        slide.subtitle_tm = request.POST.get('subtitle_tm', '')
        slide.subtitle_en = request.POST.get('subtitle_en', '')
        slide.subtitle_ru = request.POST.get('subtitle_ru', '')
        slide.link = request.POST.get('link', '')
        slide.order = int(request.POST.get('order', 0) or 0)
        if 'image' in request.FILES:
            slide.image = request.FILES['image']
        elif request.POST.get('clear_image') == '1':
            slide.image = None

        if 'image_en' in request.FILES:
            slide.image_en = request.FILES['image_en']
        elif request.POST.get('clear_image_en') == '1':
            slide.image_en = None

        if 'image_ru' in request.FILES:
            slide.image_ru = request.FILES['image_ru']
        elif request.POST.get('clear_image_ru') == '1':
            slide.image_ru = None

        if 'video' in request.FILES:
            slide.video = request.FILES['video']
        elif request.POST.get('clear_video') == '1':
            slide.video = None
        slide.save()
        messages.success(request, 'Slider üstünlikli üýtgedildi!')
        return redirect('panel_sliders')
    return render(request, 'panel/slider_form.html', {'action': 'edit', 'obj': slide})


@panel_login_required
def panel_slider_delete(request, pk):
    slide = get_object_or_404(SliderImage, pk=pk)
    if request.method == 'POST':
        slide.delete()
        messages.success(request, 'Slider öçürildi.')
    return redirect('panel_sliders')


# ─────────────────────────────────────────────
# NEWS
# ─────────────────────────────────────────────

def _parse_published_date(date_str, default=None):
    if not date_str or not str(date_str).strip():
        return default or timezone.now()
    date_str = str(date_str).strip()
    dt = parse_datetime(date_str)
    if dt is None:
        d = parse_date(date_str)
        if d:
            if default and hasattr(default, 'time'):
                base_time = default.time()
            else:
                base_time = timezone.localtime().time()
            dt = datetime.combine(d, base_time)
    if dt is not None:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    return default or timezone.now()


@panel_login_required
def panel_news(request):
    site_settings = SiteSettings.get_settings()
    if request.method == 'POST' and request.POST.get('action') == 'update_subtitle':
        site_settings.news_subtitle_tm = request.POST.get('news_subtitle_tm', site_settings.news_subtitle_tm).strip()
        site_settings.news_subtitle_en = request.POST.get('news_subtitle_en', site_settings.news_subtitle_en).strip()
        site_settings.news_subtitle_ru = request.POST.get('news_subtitle_ru', site_settings.news_subtitle_ru).strip()
        site_settings.save()
        messages.success(request, 'Täzelikler sahypasynyň düşündiriş ýazgysy üstünlikli üýtgedildi!')
        return redirect('panel_news')

    all_news = News.objects.order_by('-published_date', '-id')
    return render(request, 'panel/news.html', {'all_news': all_news, 'site_settings': site_settings})


@panel_login_required
def panel_news_add(request):
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        content_tm = request.POST.get('content_tm', '').strip()
        if not title_tm or not content_tm:
            messages.error(request, 'Türkmençe at we mazmun hökmanydyr!')
            return render(request, 'panel/news_form.html', {'action': 'add', 'post': request.POST, 'now': timezone.now()})
        source_name_tm = request.POST.get('source_name_tm', '').strip() or request.POST.get('source_name', '').strip()
        source_name_en = request.POST.get('source_name_en', '').strip()
        source_name_ru = request.POST.get('source_name_ru', '').strip()
        pub_date = _parse_published_date(request.POST.get('published_date'))
        news = News(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', ''),
            title_ru=request.POST.get('title_ru', ''),
            content_tm=content_tm,
            content_en=request.POST.get('content_en', ''),
            content_ru=request.POST.get('content_ru', ''),
            video_url=request.POST.get('video_url', '').strip(),
            source_name_tm=source_name_tm,
            source_name_en=source_name_en,
            source_name_ru=source_name_ru,
            source_name=source_name_tm,
            source_url=request.POST.get('source_url', '').strip(),
            pdf_title_tm=request.POST.get('pdf_title_tm', '').strip(),
            pdf_title_en=request.POST.get('pdf_title_en', '').strip(),
            pdf_title_ru=request.POST.get('pdf_title_ru', '').strip(),
            published_date=pub_date,
        )
        if 'image' in request.FILES:
            news.image = request.FILES['image']
        if 'image_en' in request.FILES:
            news.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            news.image_ru = request.FILES['image_ru']
        if 'video' in request.FILES:
            news.video = request.FILES['video']
        if 'pdf_file' in request.FILES:
            news.pdf_file = request.FILES['pdf_file']
        news.save()
        log_admin_action(request, 'CREATE', 'Täzelikler', object_repr=news.title_tm, object_id=news.pk, details=f"Täze habar goşuldy: {news.title_tm}")
        messages.success(request, 'Täzelik üstünlikli goşuldy!')
        return redirect('panel_news')
    return render(request, 'panel/news_form.html', {'action': 'add', 'now': timezone.now()})


@panel_login_required
def panel_news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news.title_tm = request.POST.get('title_tm', news.title_tm).strip()
        news.title_en = request.POST.get('title_en', '')
        news.title_ru = request.POST.get('title_ru', '')
        news.content_tm = request.POST.get('content_tm', news.content_tm)
        news.content_en = request.POST.get('content_en', '')
        news.content_ru = request.POST.get('content_ru', '')
        news.video_url = request.POST.get('video_url', '').strip()
        news.source_name_tm = request.POST.get('source_name_tm', '').strip()
        news.source_name_en = request.POST.get('source_name_en', '').strip()
        news.source_name_ru = request.POST.get('source_name_ru', '').strip()
        news.source_name = news.source_name_tm or request.POST.get('source_name', '').strip()
        news.source_url = request.POST.get('source_url', '').strip()
        news.pdf_title_tm = request.POST.get('pdf_title_tm', '').strip()
        news.pdf_title_en = request.POST.get('pdf_title_en', '').strip()
        news.pdf_title_ru = request.POST.get('pdf_title_ru', '').strip()
        
        if 'published_date' in request.POST:
            news.published_date = _parse_published_date(request.POST.get('published_date'), default=news.published_date)

        if 'image' in request.FILES:
            news.image = request.FILES['image']
        elif 'clear_image' in request.POST or request.POST.get('clear_image') == '1':
            news.image = None

        if 'image_en' in request.FILES:
            news.image_en = request.FILES['image_en']
        elif 'clear_image_en' in request.POST or request.POST.get('clear_image_en') == '1':
            news.image_en = None

        if 'image_ru' in request.FILES:
            news.image_ru = request.FILES['image_ru']
        elif 'clear_image_ru' in request.POST or request.POST.get('clear_image_ru') == '1':
            news.image_ru = None

        if 'video' in request.FILES:
            news.video = request.FILES['video']
        elif 'clear_video' in request.POST or request.POST.get('clear_video') == '1':
            news.video = None

        if 'pdf_file' in request.FILES:
            news.pdf_file = request.FILES['pdf_file']
        elif 'clear_pdf_file' in request.POST or request.POST.get('clear_pdf_file') == '1':
            news.pdf_file = None

        news.save()
        log_admin_action(request, 'UPDATE', 'Täzelikler', object_repr=news.title_tm, object_id=news.pk, details=f"Habar üýtgedildi: {news.title_tm}")
        messages.success(request, 'Täzelik üstünlikli üýtgedildi!')
        return redirect('panel_news')
    return render(request, 'panel/news_form.html', {'action': 'edit', 'obj': news, 'now': timezone.now()})


@panel_login_required
def panel_news_delete(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        title = news.title_tm
        news.delete()
        log_admin_action(request, 'DELETE', 'Täzelikler', object_repr=title, object_id=pk, details=f"Habar öçürildi: {title}")
        messages.success(request, 'Täzelik öçürildi.')
    return redirect('panel_news')


# ─────────────────────────────────────────────
# BILIM.TM TÄZELIKLERI (9 SANY SYNCHRONIZATION & EDIT)
# ─────────────────────────────────────────────

@panel_login_required
def panel_bilim_news(request):
    news_items = BilimNews.objects.order_by('-published_date', '-id')[:9]
    return render(request, 'panel/bilim_news.html', {'news_items': news_items})


@panel_login_required
def panel_bilim_news_sync(request):
    res = sync_bilim_news(limit=9)
    if res.get('success'):
        messages.success(request, res.get('message'))
    else:
        messages.error(request, res.get('message'))
    return redirect('panel_bilim_news')


@panel_login_required
def panel_bilim_news_add(request):
    if request.method == 'POST':
        title_tm = (request.POST.get('title_tm') or request.POST.get('title') or '').strip()
        if not title_tm:
            messages.error(request, 'Sözbasy (TM) hökmanydyr!')
            return render(request, 'panel/bilim_news_form.html', {'action': 'add', 'post': request.POST})

        item = BilimNews(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', '').strip(),
            title_ru=request.POST.get('title_ru', '').strip(),
            description_tm=(request.POST.get('description_tm') or '').strip(),
            description_en=request.POST.get('description_en', '').strip(),
            description_ru=request.POST.get('description_ru', '').strip(),
            content_tm=(request.POST.get('content_tm') or '').strip(),
            content_en=request.POST.get('content_en', '').strip(),
            content_ru=request.POST.get('content_ru', '').strip(),
            image_url=request.POST.get('image_url', '').strip(),
            source_url=request.POST.get('source_url', '').strip(),
            pdf_title_tm=request.POST.get('pdf_title_tm', '').strip(),
            pdf_title_en=request.POST.get('pdf_title_en', '').strip(),
            pdf_title_ru=request.POST.get('pdf_title_ru', '').strip(),
        )
        if 'image' in request.FILES:
            item.image = request.FILES['image']
        if 'image_en' in request.FILES:
            item.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            item.image_ru = request.FILES['image_ru']
        if 'pdf_file' in request.FILES:
            item.pdf_file = request.FILES['pdf_file']
        item.save()
        messages.success(request, 'Bilim täzeligi üstünlikli goşuldy!')
        return redirect('panel_bilim_news')
    return render(request, 'panel/bilim_news_form.html', {'action': 'add'})


@panel_login_required
def panel_bilim_news_edit(request, pk):
    item = get_object_or_404(BilimNews, pk=pk)
    if request.method == 'POST':
        item.title_tm = (request.POST.get('title_tm') or request.POST.get('title') or item.title_tm).strip()
        item.title_en = request.POST.get('title_en', item.title_en).strip()
        item.title_ru = request.POST.get('title_ru', item.title_ru).strip()

        item.description_tm = (request.POST.get('description_tm') or request.POST.get('description') or item.description_tm).strip()
        item.description_en = request.POST.get('description_en', item.description_en).strip()
        item.description_ru = request.POST.get('description_ru', item.description_ru).strip()

        item.content_tm = (request.POST.get('content_tm') or request.POST.get('content') or item.content_tm).strip()
        item.content_en = request.POST.get('content_en', item.content_en).strip()
        item.content_ru = request.POST.get('content_ru', item.content_ru).strip()

        img_url = request.POST.get('image_url', '').strip()
        if img_url:
            item.image_url = img_url
        src_url = request.POST.get('source_url', '').strip()
        if src_url:
            item.source_url = src_url
        item.pdf_title_tm = request.POST.get('pdf_title_tm', '').strip()
        item.pdf_title_en = request.POST.get('pdf_title_en', '').strip()
        item.pdf_title_ru = request.POST.get('pdf_title_ru', '').strip()

        pub_date_str = request.POST.get('published_date', '').strip()
        if pub_date_str:
            from django.utils.dateparse import parse_datetime
            parsed_d = parse_datetime(pub_date_str)
            if parsed_d:
                item.published_date = parsed_d

        try:
            item.views_count = int(request.POST.get('views_count', item.views_count))
        except (ValueError, TypeError):
            pass

        if 'image' in request.FILES:
            item.image = request.FILES['image']
        elif 'clear_image' in request.POST or request.POST.get('clear_image') == '1':
            item.image = None

        if 'image_en' in request.FILES:
            item.image_en = request.FILES['image_en']
        elif 'clear_image_en' in request.POST or request.POST.get('clear_image_en') == '1':
            item.image_en = None

        if 'image_ru' in request.FILES:
            item.image_ru = request.FILES['image_ru']
        elif 'clear_image_ru' in request.POST or request.POST.get('clear_image_ru') == '1':
            item.image_ru = None

        if 'pdf_file' in request.FILES:
            item.pdf_file = request.FILES['pdf_file']
        elif 'clear_pdf_file' in request.POST or request.POST.get('clear_pdf_file') == '1':
            item.pdf_file = None

        item.save()
        messages.success(request, 'Bilim täzeligi üstünlikli üýtgedildi!')
        return redirect('panel_bilim_news')
    return render(request, 'panel/bilim_news_form.html', {'obj': item})


@panel_login_required
def panel_bilim_news_delete(request, pk):
    item = get_object_or_404(BilimNews, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Habar öçürildi.')
    return redirect('panel_bilim_news')


# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

# Navbar bölümleriniň sanawy — sidebar we formlar üçin ulanylýar
NAV_SECTIONS = [
    ('institut',    'Institut',              'fa-solid fa-university'),
    ('ylym',        'Ylym',                  'fa-solid fa-flask'),
    ('olimpiada',   'Olimpiadalar',          'fa-solid fa-award'),
    ('baslesikler', 'Bäsleşikler',           'fa-solid fa-trophy'),
    ('halkara',     'Halkara hyzmatdaşlyk',  'fa-solid fa-globe'),
    ('dalasgar',    'Dalaşgär',              'fa-solid fa-user-graduate'),
    ('sorag_jogap', 'Sorag-jogap',           'fa-solid fa-circle-question'),
]


def get_section_cards(section_code=None):
    """Bölümdäki her bir ýokary derejeli sahypa / topar üçin aýratyn kart döredýär."""
    icon_map = {
        'Fakultetler': 'fa-solid fa-graduation-cap',
        'Kafedralar': 'fa-solid fa-chalkboard-user',
        'Saparlar': 'fa-solid fa-plane-departure',
        'Okuwlar': 'fa-solid fa-book-open-reader',
        'CirculEC': 'fa-solid fa-leaf',
        '2026': 'fa-solid fa-calendar-days',
        '2025': 'fa-solid fa-calendar-days',
        '2024': 'fa-solid fa-calendar-days',
        'Taryhy': 'fa-solid fa-landmark',
        'Görkezijiler': 'fa-solid fa-chart-line',
        'Sanly bilim': 'fa-solid fa-laptop-code',
        'Kitaphana': 'fa-solid fa-book-bookmark',
        'Wakansiýalar': 'fa-solid fa-briefcase',
        'Hepdelik sanly hasabat': 'fa-solid fa-file-contract',
        'Maksatnamalar': 'fa-solid fa-list-check',
    }

    if section_code:
        # Bölümiň esasy baş sahypasyny tapýarys (mysal üçin slug='ylym' ýa-da section='ylym')
        root_section_page = Page.objects.filter(
            Q(slug=section_code) | Q(section=section_code),
            parent__isnull=True
        ).first()

        if root_section_page:
            # Root sahypanyň gös-göni aşagyndaky ähli toparlary we sahypalary alýarys
            # Bu ýerde Page.section başgaça bolan ýagdaýynda hem (mysal üçin 'Maksatnamalar'),
            # ata sahypasy 'ylym' bolsa hökman tapylar we section täzelener.
            top_pages = list(Page.objects.filter(
                Q(parent=root_section_page) |
                (Q(section=section_code) & Q(parent__isnull=True) & ~Q(pk=root_section_page.pk))
            ).select_related('parent').prefetch_related('subpages').order_by('order', 'title_tm'))

            # Section meýdançasyny esasy bölüm kody bilen deňleşdirýäris
            for p in top_pages:
                if p.section != section_code:
                    p.section = section_code
                    p.save(update_fields=['section'])
        else:
            top_pages = list(Page.objects.filter(section=section_code, parent__isnull=True).prefetch_related('subpages').order_by('order', 'title_tm'))
            if not top_pages:
                top_pages = list(Page.objects.filter(section=section_code).prefetch_related('subpages').order_by('order', 'title_tm'))
    else:
        top_pages = list(Page.objects.filter(parent__isnull=True).prefetch_related('subpages').order_by('order', 'title_tm'))

    cards = []
    for page in top_pages:
        subpages = list(page.subpages.order_by('order', 'title_tm'))
        sub_count = len(subpages)

        cards.append({
            'title': page.title_tm,
            'parent_obj': page,
            'icon': icon_map.get(page.title_tm, 'fa-solid fa-folder-open'),
            'pages': subpages,
            'count': f"{sub_count} sany mazmun",
            'description': 'Bölümi dolandyrmak üçin aşak basyň.',
            'manage_url': f"?parent={page.pk}",
            'btn_text': "Dolandyrmak →",
            'has_subpages': sub_count > 0,
        })

    return cards


@panel_login_required
def panel_pages(request):
    pages = Page.objects.order_by('section', 'order', 'title_tm')
    cards = get_section_cards(None)
    return render(request, 'panel/pages.html', {
        'view_mode': 'overview_cards',
        'pages': pages,
        'cards': cards,
        'nav_sections': NAV_SECTIONS
    })


@panel_login_required
def panel_pages_by_section(request, section):
    """Diňe belli bir bölüme degişli sahypalary görkezýär."""
    valid_sections = [s[0] for s in NAV_SECTIONS]
    if section not in valid_sections:
        return redirect('panel_pages')

    section_label = next((s[1] for s in NAV_SECTIONS if s[0] == section), section)
    section_icon  = next((s[2] for s in NAV_SECTIONS if s[0] == section), 'fa-solid fa-file')

    parent_param = request.GET.get('parent')

    if parent_param:
        if parent_param == 'root':
            active_parent = None
            pages = Page.objects.filter(
                Q(section=section) | Q(parent__section=section),
                parent__parent=None
            ).exclude(subpages__isnull=False).order_by('order', 'title_tm')
            category_title = f"{section_label} Sahypalary"
        else:
            active_parent = get_object_or_404(Page, pk=parent_param)
            pages = Page.objects.filter(parent=active_parent).order_by('order', 'title_tm')
            category_title = active_parent.title_tm

        return render(request, 'panel/pages.html', {
            'view_mode': 'category_list',
            'pages': pages,
            'active_parent': active_parent,
            'category_title': category_title,
            'nav_sections': NAV_SECTIONS,
            'current_section': section,
            'section_label': section_label,
            'section_icon': section_icon,
        })
    else:
        cards = get_section_cards(section)
        return render(request, 'panel/pages.html', {
            'view_mode': 'overview_cards',
            'cards': cards,
            'nav_sections': NAV_SECTIONS,
            'current_section': section,
            'section_label': section_label,
            'section_icon': section_icon,
        })


@panel_login_required
def panel_page_add(request):
    all_pages = Page.objects.filter(Q(parent__parent=None) | Q(parent=None)).order_by('section', 'order', 'title_tm')
    preselect_section = request.GET.get('section', 'other')
    preselect_parent_id = request.GET.get('parent', '')
    preselect_parent = None
    if preselect_parent_id:
        preselect_parent = Page.objects.filter(pk=preselect_parent_id).first()
        if preselect_parent and preselect_parent.section:
            preselect_section = preselect_parent.section

    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        slug = request.POST.get('slug', '').strip()
        if not title_tm:
            messages.error(request, 'Sahypanyň ady (TM) hökmanydyr!')
            return render(request, 'panel/page_form.html', {
                'action': 'add', 'all_pages': all_pages,
                'post': request.POST, 'nav_sections': NAV_SECTIONS,
                'preselect_section': preselect_section,
                'preselect_parent': preselect_parent,
            })

        parent_id = request.POST.get('parent')
        if not parent_id:
            messages.error(request, 'Täze sahypa döredilende hökman bir ata sahypa (üst bölüm) saýlanmalydyr! Diňe bar bolan üst bölümleriň adyny üýtgedip bilersiňiz, täze üst bölüm goşup bolmaýar.')
            return render(request, 'panel/page_form.html', {
                'action': 'add', 'all_pages': all_pages,
                'post': request.POST, 'nav_sections': NAV_SECTIONS,
                'preselect_section': preselect_section,
                'preselect_parent': preselect_parent,
            })

        parent = Page.objects.filter(pk=parent_id).first()
        section = parent.section if parent else request.POST.get('section', 'other')

        if not slug:
            slug = generate_unique_slug(title_tm)
        elif Page.objects.filter(slug=slug).exists():
            slug = generate_unique_slug(slug)

        source_name_tm = request.POST.get('source_name_tm', '').strip() or request.POST.get('source_name', '').strip()
        source_name_en = request.POST.get('source_name_en', '').strip()
        source_name_ru = request.POST.get('source_name_ru', '').strip()

        page = Page(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', ''),
            title_ru=request.POST.get('title_ru', ''),
            slug=slug,
            section=section,
            content_tm=request.POST.get('content_tm', ''),
            content_en=request.POST.get('content_en', ''),
            content_ru=request.POST.get('content_ru', ''),
            show_in_tm=bool(request.POST.get('show_in_tm')),
            show_in_en=bool(request.POST.get('show_in_en')),
            show_in_ru=bool(request.POST.get('show_in_ru')),
            source_name_tm=source_name_tm,
            source_name_en=source_name_en,
            source_name_ru=source_name_ru,
            source_name=source_name_tm,
            source_url=request.POST.get('source_url', '').strip(),
            pdf_title_tm=request.POST.get('pdf_title_tm', '').strip(),
            pdf_title_en=request.POST.get('pdf_title_en', '').strip(),
            pdf_title_ru=request.POST.get('pdf_title_ru', '').strip(),
            parent=parent,
            order=int(request.POST.get('order', 0) or 0),
        )
        if 'image' in request.FILES:
            page.image = request.FILES['image']
        if 'image_en' in request.FILES:
            page.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            page.image_ru = request.FILES['image_ru']
        if 'banner_image' in request.FILES:
            page.banner_image = request.FILES['banner_image']
        if 'pdf_file' in request.FILES:
            page.pdf_file = request.FILES['pdf_file']
        page.save()
        log_admin_action(request, 'CREATE', 'Sahypalar', object_repr=page.title_tm, object_id=page.pk, details=f"Täze sahypa goşuldy: {page.title_tm} ({page.section})")
        messages.success(request, 'Sahypa üstünlikli goşuldy!')
        if parent:
            is_root = (parent.slug == section and parent.parent is None)
            if not is_root:
                return redirect(f"{reverse('panel_pages_by_section', kwargs={'section': section})}?parent={parent.pk}")
        return redirect('panel_pages_by_section', section=section)
    return render(request, 'panel/page_form.html', {
        'action': 'add',
        'all_pages': all_pages,
        'nav_sections': NAV_SECTIONS,
        'preselect_section': preselect_section,
        'preselect_parent': preselect_parent,
    })


@panel_login_required
def panel_page_edit(request, pk):
    page = get_object_or_404(Page, pk=pk)
    all_pages = Page.objects.filter(Q(parent__parent=None) | Q(parent=None)).exclude(pk=pk).order_by('section', 'order', 'title_tm')
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', page.title_tm).strip()
        slug = request.POST.get('slug', '').strip()
        
        if not title_tm:
            messages.error(request, 'Sahypanyň ady (TM) hökmanydyr!')
            return render(request, 'panel/page_form.html', {
                'action': 'edit', 'obj': page, 'all_pages': all_pages,
                'nav_sections': NAV_SECTIONS,
            })

        if not slug:
            slug = generate_unique_slug(title_tm, current_pk=page.pk)
        elif Page.objects.filter(slug=slug).exclude(pk=pk).exists():
            slug = generate_unique_slug(slug, current_pk=page.pk)

        page.title_tm = title_tm
        page.title_en = request.POST.get('title_en', '')
        page.title_ru = request.POST.get('title_ru', '')
        page.slug = slug
        page.section = request.POST.get('section', page.section)
        page.content_tm = request.POST.get('content_tm', '')
        page.content_en = request.POST.get('content_en', '')
        page.content_ru = request.POST.get('content_ru', '')
        page.show_in_tm = bool(request.POST.get('show_in_tm'))
        page.show_in_en = bool(request.POST.get('show_in_en'))
        page.show_in_ru = bool(request.POST.get('show_in_ru'))
        page.source_name_tm = request.POST.get('source_name_tm', '').strip()
        page.source_name_en = request.POST.get('source_name_en', '').strip()
        page.source_name_ru = request.POST.get('source_name_ru', '').strip()
        page.source_name = page.source_name_tm or request.POST.get('source_name', '').strip()
        page.source_url = request.POST.get('source_url', '').strip()
        page.pdf_title_tm = request.POST.get('pdf_title_tm', '').strip()
        page.pdf_title_en = request.POST.get('pdf_title_en', '').strip()
        page.pdf_title_ru = request.POST.get('pdf_title_ru', '').strip()
        if page.parent is not None:
            parent_id = request.POST.get('parent')
            if parent_id:
                page.parent = Page.objects.filter(pk=parent_id).first()
        page.order = int(request.POST.get('order', 0) or 0)
        
        # TM Image
        if 'image' in request.FILES:
            page.image = request.FILES['image']
        elif request.POST.get('clear_image') == '1':
            page.image = None

        # EN Image
        if 'image_en' in request.FILES:
            page.image_en = request.FILES['image_en']
        elif request.POST.get('clear_image_en') == '1':
            page.image_en = None

        # RU Image
        if 'image_ru' in request.FILES:
            page.image_ru = request.FILES['image_ru']
        elif request.POST.get('clear_image_ru') == '1':
            page.image_ru = None

        # Banner Image
        if 'banner_image' in request.FILES:
            page.banner_image = request.FILES['banner_image']
        elif request.POST.get('clear_banner_image') == '1':
            page.banner_image = None

        if 'pdf_file' in request.FILES:
            page.pdf_file = request.FILES['pdf_file']
        elif request.POST.get('clear_pdf_file') == '1':
            page.pdf_file = None

        page.save()
        log_admin_action(request, 'UPDATE', 'Sahypalar', object_repr=page.title_tm, object_id=page.pk, details=f"Sahypa üýtgedildi: {page.title_tm} ({page.section})")
        messages.success(request, 'Sahypa üstünlikli üýtgedildi!')
        if page.parent:
            is_root = (page.parent.slug == page.section and page.parent.parent is None)
            if not is_root:
                return redirect(f"{reverse('panel_pages_by_section', kwargs={'section': page.section})}?parent={page.parent.pk}")
        return redirect('panel_pages_by_section', section=page.section)
    return render(request, 'panel/page_form.html', {
        'action': 'edit',
        'obj': page,
        'all_pages': all_pages,
        'nav_sections': NAV_SECTIONS,
    })


@panel_login_required
def panel_page_delete(request, pk):
    page = get_object_or_404(Page, pk=pk)
    section = page.section
    parent = page.parent
    if request.method == 'POST':
        title = page.title_tm
        page.delete()
        log_admin_action(request, 'DELETE', 'Sahypalar', object_repr=title, object_id=pk, details=f"Sahypa öçürildi: {title}")
        messages.success(request, 'Sahypa öçürildi.')
    if parent:
        is_root = (parent.slug == section and parent.parent is None)
        if not is_root:
            return redirect(f"{reverse('panel_pages_by_section', kwargs={'section': section})}?parent={parent.pk}")
    return redirect('panel_pages_by_section', section=section)


# ─────────────────────────────────────────────
# FACULTIES
# ─────────────────────────────────────────────

@panel_login_required
def panel_faculties(request):
    faculties = Faculty.objects.prefetch_related('departments')
    return render(request, 'panel/faculties.html', {'faculties': faculties})


@panel_login_required
def panel_faculty_add(request):
    if request.method == 'POST':
        name_tm = request.POST.get('name_tm', '').strip()
        description_tm = request.POST.get('description_tm', '').strip()
        if not name_tm or not description_tm:
            messages.error(request, 'At we beýan hökmanydyr!')
            return render(request, 'panel/faculty_form.html', {'action': 'add', 'post': request.POST})
        faculty = Faculty(
            name_tm=name_tm,
            name_en=request.POST.get('name_en', ''),
            name_ru=request.POST.get('name_ru', ''),
            description_tm=description_tm,
            description_en=request.POST.get('description_en', ''),
            description_ru=request.POST.get('description_ru', ''),
            dean_name_tm=request.POST.get('dean_name_tm', ''),
            dean_name_en=request.POST.get('dean_name_en', ''),
            dean_name_ru=request.POST.get('dean_name_ru', ''),
        )
        if 'image' in request.FILES:
            faculty.image = request.FILES['image']
        if 'image_en' in request.FILES:
            faculty.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            faculty.image_ru = request.FILES['image_ru']
        faculty.save()
        log_admin_action(request, 'CREATE', 'Fakultetler', object_repr=faculty.name_tm, object_id=faculty.pk, details=f"Täze fakultet goşuldy: {faculty.name_tm}, Dekan: {faculty.dean_name_tm}")
        messages.success(request, 'Fakultet üstünlikli goşuldy!')
        return redirect('panel_faculties')
    return render(request, 'panel/faculty_form.html', {'action': 'add'})


@panel_login_required
def panel_faculty_edit(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        faculty.name_tm = request.POST.get('name_tm', faculty.name_tm).strip()
        faculty.name_en = request.POST.get('name_en', '')
        faculty.name_ru = request.POST.get('name_ru', '')
        faculty.description_tm = request.POST.get('description_tm', faculty.description_tm)
        faculty.description_en = request.POST.get('description_en', '')
        faculty.description_ru = request.POST.get('description_ru', '')
        faculty.dean_name_tm = request.POST.get('dean_name_tm', '')
        faculty.dean_name_en = request.POST.get('dean_name_en', '')
        faculty.dean_name_ru = request.POST.get('dean_name_ru', '')
        
        if 'image' in request.FILES:
            faculty.image = request.FILES['image']
        elif request.POST.get('clear_image') == '1':
            faculty.image = None

        if 'image_en' in request.FILES:
            faculty.image_en = request.FILES['image_en']
        elif request.POST.get('clear_image_en') == '1':
            faculty.image_en = None

        if 'image_ru' in request.FILES:
            faculty.image_ru = request.FILES['image_ru']
        elif request.POST.get('clear_image_ru') == '1':
            faculty.image_ru = None

        faculty.save()
        log_admin_action(request, 'UPDATE', 'Fakultetler', object_repr=faculty.name_tm, object_id=faculty.pk, details=f"Fakultet üýtgedildi: {faculty.name_tm}, Dekan: {faculty.dean_name_tm}")
        messages.success(request, 'Fakultet üstünlikli üýtgedildi!')
        return redirect('panel_faculties')
    return render(request, 'panel/faculty_form.html', {'action': 'edit', 'obj': faculty})


@panel_login_required
def panel_faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        name = faculty.name_tm
        faculty.delete()
        log_admin_action(request, 'DELETE', 'Fakultetler', object_repr=name, object_id=pk, details=f"Fakultet öçürildi: {name}")
        messages.success(request, 'Fakultet öçürildi.')
    return redirect('panel_faculties')


# ─────────────────────────────────────────────
# DEPARTMENTS
# ─────────────────────────────────────────────

@panel_login_required
def panel_departments(request):
    faculties = Faculty.objects.all().order_by('name_tm')
    faculty_id = request.GET.get('faculty', '').strip()
    departments = Department.objects.select_related('faculty').order_by('faculty__name_tm', 'name_tm')
    all_departments_count = departments.count()
    if faculty_id:
        departments = departments.filter(faculty_id=faculty_id)
    return render(request, 'panel/departments.html', {
        'departments': departments,
        'faculties': faculties,
        'selected_faculty_id': faculty_id,
        'all_departments_count': all_departments_count,
    })


@panel_login_required
def panel_department_add(request):
    faculties = Faculty.objects.all().order_by('name_tm')
    selected_faculty_id = request.GET.get('faculty', '').strip()
    if request.method == 'POST':
        name_tm = request.POST.get('name_tm', '').strip()
        description_tm = request.POST.get('description_tm', '').strip()
        faculty_id = request.POST.get('faculty')
        if not name_tm or not description_tm or not faculty_id:
            messages.error(request, 'At, beýan we fakultet hökmanydyr!')
            return render(request, 'panel/department_form.html', {'action': 'add', 'faculties': faculties, 'post': request.POST, 'selected_faculty_id': selected_faculty_id})
        faculty = get_object_or_404(Faculty, pk=faculty_id)
        dept = Department(
            faculty=faculty,
            name_tm=name_tm,
            name_en=request.POST.get('name_en', ''),
            name_ru=request.POST.get('name_ru', ''),
            description_tm=description_tm,
            description_en=request.POST.get('description_en', ''),
            description_ru=request.POST.get('description_ru', ''),
            head_name_tm=request.POST.get('head_name_tm', ''),
            head_name_en=request.POST.get('head_name_en', ''),
            head_name_ru=request.POST.get('head_name_ru', ''),
        )
        if 'image' in request.FILES:
            dept.image = request.FILES['image']
        if 'image_en' in request.FILES:
            dept.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            dept.image_ru = request.FILES['image_ru']
        dept.save()
        log_admin_action(request, 'CREATE', 'Kafedralar', object_repr=dept.name_tm, object_id=dept.pk, details=f"Täze kafedra goşuldy: {dept.name_tm} ({dept.faculty.name_tm}), Müdir: {dept.head_name_tm}")
        messages.success(request, 'Kafedra üstünlikli goşuldy!')
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('panel_departments')
    return render(request, 'panel/department_form.html', {'action': 'add', 'faculties': faculties, 'selected_faculty_id': selected_faculty_id})


@panel_login_required
def panel_department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    faculties = Faculty.objects.all().order_by('name_tm')
    if request.method == 'POST':
        dept.name_tm = request.POST.get('name_tm', dept.name_tm).strip()
        dept.name_en = request.POST.get('name_en', '')
        dept.name_ru = request.POST.get('name_ru', '')
        dept.description_tm = request.POST.get('description_tm', dept.description_tm)
        dept.description_en = request.POST.get('description_en', '')
        dept.description_ru = request.POST.get('description_ru', '')
        dept.head_name_tm = request.POST.get('head_name_tm', '')
        dept.head_name_en = request.POST.get('head_name_en', '')
        dept.head_name_ru = request.POST.get('head_name_ru', '')
        faculty_id = request.POST.get('faculty')
        if faculty_id:
            dept.faculty = get_object_or_404(Faculty, pk=faculty_id)

        if 'image' in request.FILES:
            dept.image = request.FILES['image']
        elif request.POST.get('clear_image') == '1':
            dept.image = None

        if 'image_en' in request.FILES:
            dept.image_en = request.FILES['image_en']
        elif request.POST.get('clear_image_en') == '1':
            dept.image_en = None

        if 'image_ru' in request.FILES:
            dept.image_ru = request.FILES['image_ru']
        elif request.POST.get('clear_image_ru') == '1':
            dept.image_ru = None

        dept.save()
        log_admin_action(request, 'UPDATE', 'Kafedralar', object_repr=dept.name_tm, object_id=dept.pk, details=f"Kafedra üýtgedildi: {dept.name_tm} ({dept.faculty.name_tm}), Müdir: {dept.head_name_tm}")
        messages.success(request, 'Kafedra üstünlikli üýtgedildi!')
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('panel_departments')
    return render(request, 'panel/department_form.html', {'action': 'edit', 'obj': dept, 'faculties': faculties})


@panel_login_required
def panel_department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = dept.name_tm
        dept.delete()
        log_admin_action(request, 'DELETE', 'Kafedralar', object_repr=name, object_id=pk, details=f"Kafedra öçürildi: {name}")
        messages.success(request, 'Kafedra öçürildi.')
    return redirect('panel_departments')


# ─────────────────────────────────────────────
# DOCUMENTS
# ─────────────────────────────────────────────

@panel_login_required
def panel_documents(request):
    q = request.GET.get('q', '').strip()
    docs = Document.objects.order_by('-uploaded_at')
    if q:
        docs = docs.filter(
            Q(title_tm__icontains=q) |
            Q(title_en__icontains=q) |
            Q(title_ru__icontains=q) |
            Q(file__icontains=q)
        )
    return render(request, 'panel/documents.html', {
        'docs': docs,
        'search_query': q,
    })


@panel_login_required
def panel_document_add(request):
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        category = request.POST.get('category', '').strip() or 'Resminama'
        if not title_tm or 'file' not in request.FILES:
            messages.error(request, 'At we faýl hökmanydyr!')
            return render(request, 'panel/document_form.html', {
                'post': request.POST, 'action': 'add'
            })
        doc = Document(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', ''),
            title_ru=request.POST.get('title_ru', ''),
            category=category,
            file=request.FILES['file'],
        )
        if 'image' in request.FILES:
            doc.image = request.FILES['image']
        if 'image_en' in request.FILES:
            doc.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            doc.image_ru = request.FILES['image_ru']
        doc.save()
        messages.success(request, 'Resminama üstünlikli goşuldy!')
        return redirect('panel_documents')
    return render(request, 'panel/document_form.html', {'action': 'add'})


@panel_login_required
def panel_document_edit(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        doc.title_tm = request.POST.get('title_tm', doc.title_tm).strip()
        doc.title_en = request.POST.get('title_en', '')
        doc.title_ru = request.POST.get('title_ru', '')
        doc.category = request.POST.get('category', doc.category)
        if 'file' in request.FILES:
            doc.file = request.FILES['file']
        if 'image' in request.FILES:
            doc.image = request.FILES['image']
        elif request.POST.get('clear_image') == '1':
            doc.image = None

        if 'image_en' in request.FILES:
            doc.image_en = request.FILES['image_en']
        elif request.POST.get('clear_image_en') == '1':
            doc.image_en = None

        if 'image_ru' in request.FILES:
            doc.image_ru = request.FILES['image_ru']
        elif request.POST.get('clear_image_ru') == '1':
            doc.image_ru = None

        doc.save()
        messages.success(request, 'Resminama üstünlikli üýtgedildi!')
        return redirect('panel_documents')
    return render(request, 'panel/document_form.html', {'obj': doc, 'action': 'edit'})


@panel_login_required
def panel_document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        doc.delete()
        messages.success(request, 'Resminama öçürildi.')
    return redirect('panel_documents')


def serialize_document_for_panel(doc):
    """Serialize Document model into clean JSON for TinyMCE & panel pickers."""
    try:
        file_url = doc.file.url if doc.file else ''
    except Exception:
        file_url = ''
    try:
        file_name = os.path.basename(doc.file.name) if doc.file else ''
    except Exception:
        file_name = ''

    ext = os.path.splitext(file_name)[1].lower().replace('.', '')
    cat = file_category(doc.file) if doc.file else 'other'

    size_str = ''
    if doc.file:
        try:
            sz = doc.file.size
            if sz < 1024:
                size_str = f"{sz} B"
            elif sz < 1024 * 1024:
                size_str = f"{sz / 1024:.1f} KB"
            else:
                size_str = f"{sz / (1024 * 1024):.1f} MB"
        except Exception:
            size_str = ''

    return {
        'id': doc.pk,
        'title_tm': doc.title_tm,
        'title_en': doc.title_en or doc.title_tm,
        'title_ru': doc.title_ru or doc.title_tm,
        'category': doc.category,
        'category_display': doc.get_category_display(),
        'file_url': file_url,
        'page_url': f'/document/{doc.pk}/',
        'file_name': file_name,
        'ext': ext,
        'cat_type': cat,
        'icon': file_icon(doc.file),
        'color': file_color(doc.file),
        'bg_color': file_bg_color(doc.file),
        'label_tm': file_category_label(doc.file, 'tm'),
        'size': size_str,
        'date': doc.uploaded_at.strftime('%d.%m.%Y'),
    }


@panel_login_required
def panel_api_documents(request):
    """JSON API to search and list documents for Mazmuny TinyMCE picker."""
    q = request.GET.get('q', '').strip()
    docs = Document.objects.all().order_by('-uploaded_at')
    if q:
        docs = docs.filter(
            Q(title_tm__icontains=q) |
            Q(title_en__icontains=q) |
            Q(title_ru__icontains=q) |
            Q(file__icontains=q)
        )
    items = [serialize_document_for_panel(d) for d in docs[:150]]
    return JsonResponse({'status': 'ok', 'documents': items, 'count': len(items)})


@panel_login_required
def panel_api_document_quick_upload(request):
    """Direct quick-upload endpoint from Mazmuny TinyMCE modal."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Diňe POST goldanylýar'}, status=405)

    title_tm = request.POST.get('title_tm', '').strip()
    category = request.POST.get('category', 'Resminama').strip() or 'Resminama'
    title_en = request.POST.get('title_en', '').strip()
    title_ru = request.POST.get('title_ru', '').strip()

    if not title_tm:
        return JsonResponse({'status': 'error', 'message': 'Resminamanyň ady (TM) hökmanydyr!'}, status=400)

    if 'file' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'Faýl saýlanmadyk!'}, status=400)

    uploaded_file = request.FILES['file']
    doc = Document(
        title_tm=title_tm,
        title_en=title_en,
        title_ru=title_ru,
        category=category,
        file=uploaded_file,
    )
    doc.save()

    return JsonResponse({
        'status': 'ok',
        'message': 'Resminama üstünlikli ýüklendi!',
        'document': serialize_document_for_panel(doc)
    })


# ─────────────────────────────────────────────
# OLYMPIADS
# ─────────────────────────────────────────────

@panel_login_required
def panel_olympiads(request):
    olympiads = Olympiad.objects.order_by('-year', 'title_tm')
    return render(request, 'panel/olympiads.html', {'olympiads': olympiads})


@panel_login_required
def panel_olympiad_add(request):
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        if not title_tm:
            messages.error(request, 'At hökmanydyr!')
            return render(request, 'panel/olympiad_form.html', {'action': 'add', 'post': request.POST})
        olympiad = Olympiad(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', ''),
            title_ru=request.POST.get('title_ru', ''),
            year=int(request.POST.get('year', timezone.now().year) or timezone.now().year),
            description_tm=request.POST.get('description_tm', ''),
            description_en=request.POST.get('description_en', ''),
            description_ru=request.POST.get('description_ru', ''),
        )
        if 'results_pdf' in request.FILES:
            olympiad.results_pdf = request.FILES['results_pdf']
        olympiad.save()
        messages.success(request, 'Olimpiada üstünlikli goşuldy!')
        return redirect('panel_olympiads')
    return render(request, 'panel/olympiad_form.html', {'action': 'add'})


@panel_login_required
def panel_olympiad_edit(request, pk):
    olympiad = get_object_or_404(Olympiad, pk=pk)
    if request.method == 'POST':
        olympiad.title_tm = request.POST.get('title_tm', olympiad.title_tm).strip()
        olympiad.title_en = request.POST.get('title_en', '')
        olympiad.title_ru = request.POST.get('title_ru', '')
        olympiad.year = int(request.POST.get('year', olympiad.year) or olympiad.year)
        olympiad.description_tm = request.POST.get('description_tm', '')
        olympiad.description_en = request.POST.get('description_en', '')
        olympiad.description_ru = request.POST.get('description_ru', '')
        if 'results_pdf' in request.FILES:
            olympiad.results_pdf = request.FILES['results_pdf']
        olympiad.save()
        messages.success(request, 'Olimpiada üstünlikli üýtgedildi!')
        return redirect('panel_olympiads')
    return render(request, 'panel/olympiad_form.html', {'action': 'edit', 'obj': olympiad})


@panel_login_required
def panel_olympiad_delete(request, pk):
    olympiad = get_object_or_404(Olympiad, pk=pk)
    if request.method == 'POST':
        olympiad.delete()
        messages.success(request, 'Olimpiada öçürildi.')
    return redirect('panel_olympiads')


# ─────────────────────────────────────────────
# PARTNERS
# ─────────────────────────────────────────────

@panel_login_required
def panel_partners(request):
    partners = Partner.objects.all()
    return render(request, 'panel/partners.html', {'partners': partners})


@panel_login_required
def panel_partner_add(request):
    if request.method == 'POST':
        name_tm = request.POST.get('name_tm', '').strip()
        if not name_tm or 'logo' not in request.FILES:
            messages.error(request, 'At we logo hökmanydyr!')
            return render(request, 'panel/partner_form.html', {'action': 'add', 'post': request.POST})
        partner = Partner(
            name_tm=name_tm,
            name_en=request.POST.get('name_en', ''),
            name_ru=request.POST.get('name_ru', ''),
            country_tm=request.POST.get('country_tm', ''),
            country_en=request.POST.get('country_en', ''),
            country_ru=request.POST.get('country_ru', ''),
            logo=request.FILES['logo'],
        )
        partner.save()
        messages.success(request, 'Hyzmatdaş üstünlikli goşuldy!')
        return redirect('panel_partners')
    return render(request, 'panel/partner_form.html', {'action': 'add'})


@panel_login_required
def panel_partner_edit(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        partner.name_tm = request.POST.get('name_tm', partner.name_tm).strip()
        partner.name_en = request.POST.get('name_en', '')
        partner.name_ru = request.POST.get('name_ru', '')
        partner.country_tm = request.POST.get('country_tm', '')
        partner.country_en = request.POST.get('country_en', '')
        partner.country_ru = request.POST.get('country_ru', '')
        if 'logo' in request.FILES:
            partner.logo = request.FILES['logo']
        partner.save()
        messages.success(request, 'Hyzmatdaş üstünlikli üýtgedildi!')
        return redirect('panel_partners')
    return render(request, 'panel/partner_form.html', {'action': 'edit', 'obj': partner})


@panel_login_required
def panel_partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        partner.delete()
        messages.success(request, 'Hyzmatdaş öçürildi.')
    return redirect('panel_partners')


# ─────────────────────────────────────────────
# MESSAGES
# ─────────────────────────────────────────────

@panel_login_required
def panel_messages(request):
    all_messages = ContactMessage.objects.order_by('-created_at')
    return render(request, 'panel/messages.html', {'all_messages': all_messages})


@panel_login_required
def panel_message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        msg.delete()
        messages.success(request, 'Hat öçürildi.')
    return redirect('panel_messages')


@panel_login_required
def panel_message_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return redirect('panel_messages')


# ─────────────────────────────────────────────
# SITE SETTINGS
# ─────────────────────────────────────────────

@panel_login_required
def panel_settings(request):
    site_settings = SiteSettings.get_settings()
    if request.method == 'POST':
        site_settings.stat_books = request.POST.get('stat_books', site_settings.stat_books)
        site_settings.stat_majors = request.POST.get('stat_majors', site_settings.stat_majors)
        site_settings.stat_teachers = request.POST.get('stat_teachers', site_settings.stat_teachers)
        site_settings.stat_students = request.POST.get('stat_students', site_settings.stat_students)
        
        if 'stat_books_icon' in request.FILES:
            site_settings.stat_books_icon = request.FILES['stat_books_icon']
        if 'stat_majors_icon' in request.FILES:
            site_settings.stat_majors_icon = request.FILES['stat_majors_icon']
        if 'stat_teachers_icon' in request.FILES:
            site_settings.stat_teachers_icon = request.FILES['stat_teachers_icon']
        if 'stat_students_icon' in request.FILES:
            site_settings.stat_students_icon = request.FILES['stat_students_icon']
            
        site_settings.address_tm = request.POST.get('address_tm', '')
        site_settings.address_en = request.POST.get('address_en', '')
        site_settings.address_ru = request.POST.get('address_ru', '')
        site_settings.phone = request.POST.get('phone', '')
        site_settings.phone2 = request.POST.get('phone2', '')
        site_settings.email = request.POST.get('email', '')
        site_settings.facebook_url = request.POST.get('facebook_url', '')
        site_settings.twitter_url = request.POST.get('twitter_url', '')
        site_settings.linkedin_url = request.POST.get('linkedin_url', '')
        site_settings.instagram_url = request.POST.get('instagram_url', '')
        site_settings.youtube_url = request.POST.get('youtube_url', '')
        site_settings.telegram_url = request.POST.get('telegram_url', '')
        site_settings.tiktok_url = request.POST.get('tiktok_url', '')

        # Footer 1-nji sütün: Brand & Düşündiriş
        site_settings.footer_title_tm = request.POST.get('footer_title_tm', site_settings.footer_title_tm).strip()
        site_settings.footer_title_en = request.POST.get('footer_title_en', site_settings.footer_title_en).strip()
        site_settings.footer_title_ru = request.POST.get('footer_title_ru', site_settings.footer_title_ru).strip()
        site_settings.footer_desc_tm = request.POST.get('footer_desc_tm', site_settings.footer_desc_tm).strip()
        site_settings.footer_desc_en = request.POST.get('footer_desc_en', site_settings.footer_desc_en).strip()
        site_settings.footer_desc_ru = request.POST.get('footer_desc_ru', site_settings.footer_desc_ru).strip()

        # Footer 2-nji sütün: Institut & Çykgytlar
        site_settings.footer_col2_title_tm = request.POST.get('footer_col2_title_tm', site_settings.footer_col2_title_tm).strip()
        site_settings.footer_col2_title_en = request.POST.get('footer_col2_title_en', site_settings.footer_col2_title_en).strip()
        site_settings.footer_col2_title_ru = request.POST.get('footer_col2_title_ru', site_settings.footer_col2_title_ru).strip()

        site_settings.footer_col2_l1_text_tm = request.POST.get('footer_col2_l1_text_tm', site_settings.footer_col2_l1_text_tm).strip()
        site_settings.footer_col2_l1_text_en = request.POST.get('footer_col2_l1_text_en', site_settings.footer_col2_l1_text_en).strip()
        site_settings.footer_col2_l1_text_ru = request.POST.get('footer_col2_l1_text_ru', site_settings.footer_col2_l1_text_ru).strip()
        site_settings.footer_col2_l1_url = request.POST.get('footer_col2_l1_url', site_settings.footer_col2_l1_url).strip()

        site_settings.footer_col2_l2_text_tm = request.POST.get('footer_col2_l2_text_tm', site_settings.footer_col2_l2_text_tm).strip()
        site_settings.footer_col2_l2_text_en = request.POST.get('footer_col2_l2_text_en', site_settings.footer_col2_l2_text_en).strip()
        site_settings.footer_col2_l2_text_ru = request.POST.get('footer_col2_l2_text_ru', site_settings.footer_col2_l2_text_ru).strip()
        site_settings.footer_col2_l2_url = request.POST.get('footer_col2_l2_url', site_settings.footer_col2_l2_url).strip()

        site_settings.footer_col2_l3_text_tm = request.POST.get('footer_col2_l3_text_tm', site_settings.footer_col2_l3_text_tm).strip()
        site_settings.footer_col2_l3_text_en = request.POST.get('footer_col2_l3_text_en', site_settings.footer_col2_l3_text_en).strip()
        site_settings.footer_col2_l3_text_ru = request.POST.get('footer_col2_l3_text_ru', site_settings.footer_col2_l3_text_ru).strip()
        site_settings.footer_col2_l3_url = request.POST.get('footer_col2_l3_url', site_settings.footer_col2_l3_url).strip()

        site_settings.footer_col2_l4_text_tm = request.POST.get('footer_col2_l4_text_tm', site_settings.footer_col2_l4_text_tm).strip()
        site_settings.footer_col2_l4_text_en = request.POST.get('footer_col2_l4_text_en', site_settings.footer_col2_l4_text_en).strip()
        site_settings.footer_col2_l4_text_ru = request.POST.get('footer_col2_l4_text_ru', site_settings.footer_col2_l4_text_ru).strip()
        site_settings.footer_col2_l4_url = request.POST.get('footer_col2_l4_url', site_settings.footer_col2_l4_url).strip()

        # Footer 3-nji sütün: Fakultetler
        site_settings.footer_col3_title_tm = request.POST.get('footer_col3_title_tm', site_settings.footer_col3_title_tm).strip()
        site_settings.footer_col3_title_en = request.POST.get('footer_col3_title_en', site_settings.footer_col3_title_en).strip()
        site_settings.footer_col3_title_ru = request.POST.get('footer_col3_title_ru', site_settings.footer_col3_title_ru).strip()

        # Footer 4-nji sütün: Habarlaşmak
        site_settings.footer_col4_title_tm = request.POST.get('footer_col4_title_tm', site_settings.footer_col4_title_tm).strip()
        site_settings.footer_col4_title_en = request.POST.get('footer_col4_title_en', site_settings.footer_col4_title_en).strip()
        site_settings.footer_col4_title_ru = request.POST.get('footer_col4_title_ru', site_settings.footer_col4_title_ru).strip()

        # Footer Bottom: Copyright
        site_settings.copyright_text_tm = request.POST.get('copyright_text_tm', site_settings.copyright_text_tm).strip()
        site_settings.copyright_text_en = request.POST.get('copyright_text_en', site_settings.copyright_text_en).strip()
        site_settings.copyright_text_ru = request.POST.get('copyright_text_ru', site_settings.copyright_text_ru).strip()

        # Institute Branding / Logo & Name
        site_settings.logo_title_tm = request.POST.get('logo_title_tm', site_settings.logo_title_tm).strip()
        site_settings.logo_subtitle_tm = request.POST.get('logo_subtitle_tm', site_settings.logo_subtitle_tm).strip()
        site_settings.logo_title_en = request.POST.get('logo_title_en', site_settings.logo_title_en).strip()
        site_settings.logo_subtitle_en = request.POST.get('logo_subtitle_en', site_settings.logo_subtitle_en).strip()
        site_settings.logo_title_ru = request.POST.get('logo_title_ru', site_settings.logo_title_ru).strip()
        site_settings.logo_subtitle_ru = request.POST.get('logo_subtitle_ru', site_settings.logo_subtitle_ru).strip()

        if 'logo' in request.FILES:
            site_settings.logo = request.FILES['logo']
        elif request.POST.get('clear_logo') == '1':
            site_settings.logo = None

        if 'stats_bg_image' in request.FILES:
            site_settings.stats_bg_image = request.FILES['stats_bg_image']

        if 'page_banner_image' in request.FILES:
            site_settings.page_banner_image = request.FILES['page_banner_image']
        elif request.POST.get('clear_page_banner_image') == '1':
            site_settings.page_banner_image = None

        # News Page Header & Subtitle
        site_settings.news_title_tm = request.POST.get('news_title_tm', site_settings.news_title_tm).strip()
        site_settings.news_title_en = request.POST.get('news_title_en', site_settings.news_title_en).strip()
        site_settings.news_title_ru = request.POST.get('news_title_ru', site_settings.news_title_ru).strip()
        site_settings.news_subtitle_tm = request.POST.get('news_subtitle_tm', site_settings.news_subtitle_tm).strip()
        site_settings.news_subtitle_en = request.POST.get('news_subtitle_en', site_settings.news_subtitle_en).strip()
        site_settings.news_subtitle_ru = request.POST.get('news_subtitle_ru', site_settings.news_subtitle_ru).strip()

        # IP Restriction
        new_ip_restriction = request.POST.get('ip_restriction_enabled') == '1'
        if new_ip_restriction and not site_settings.ip_restriction_enabled:
            current_ip = get_client_ip(request)
            if not AllowedIP.objects.filter(is_active=True).exists():
                AllowedIP.objects.create(ip_address=current_ip, label="Administrator (Awtomatiki goşuldy)", is_active=True)
                messages.info(request, f'Ulgamdan çykyp galmazlygyňyz üçin häzirki IP salgyňyz ("{current_ip}") awtomatiki goşuldy.')
        site_settings.ip_restriction_enabled = new_ip_restriction

        site_settings.save()
        messages.success(request, 'Sazlamalar üstünlikli ýatda saklanyldy!')
        return redirect('panel_settings')
    return render(request, 'panel/settings.html', {'site_settings': site_settings})


# ─────────────────────────────────────────────
# LIBRARY CATEGORIES (ŽURNAL KATEGORIÝALARY)
# ─────────────────────────────────────────────

@panel_login_required
def panel_library_categories(request):
    if request.method == 'POST' and request.POST.get('action') == 'delete_selected':
        selected_ids = request.POST.getlist('selected_items')
        if selected_ids:
            count = LibraryCategory.objects.filter(id__in=selected_ids).delete()[0]
            messages.success(request, f'{count} sany kategoriýa üstünlikli pozuldy.')
        return redirect('panel_library_categories')

    categories = LibraryCategory.objects.all().order_by('order', 'id')
    return render(request, 'panel/library_categories.html', {'categories': categories})


@panel_login_required
def panel_library_category_add(request):
    if request.method == 'POST':
        name_tm = request.POST.get('name_tm', '').strip()
        if not name_tm:
            messages.error(request, 'Kategoriýanyň ady hökmanydyr!')
            return render(request, 'panel/library_category_form.html', {'action': 'add', 'post': request.POST})

        cat = LibraryCategory(
            name_tm=name_tm,
            name_en=request.POST.get('name_en', '').strip(),
            name_ru=request.POST.get('name_ru', '').strip(),
            order=int(request.POST.get('order', 0) or 0)
        )
        if 'icon' in request.FILES:
            cat.icon = request.FILES['icon']
        cat.save()
        messages.success(request, 'Neşir kategoriýasy üstünlikli goşuldy!')
        return redirect('panel_library_categories')
    return render(request, 'panel/library_category_form.html', {'action': 'add'})


@panel_login_required
def panel_library_category_edit(request, pk):
    cat = get_object_or_404(LibraryCategory, pk=pk)
    if request.method == 'POST':
        name_tm = request.POST.get('name_tm', '').strip()
        if not name_tm:
            messages.error(request, 'Kategoriýanyň ady hökmanydyr!')
            return render(request, 'panel/library_category_form.html', {'action': 'edit', 'obj': cat})

        cat.name_tm = name_tm
        cat.name_en = request.POST.get('name_en', '').strip()
        cat.name_ru = request.POST.get('name_ru', '').strip()
        cat.order = int(request.POST.get('order', 0) or 0)

        if request.POST.get('clear_icon') == '1':
            cat.icon = None
        elif 'icon' in request.FILES:
            cat.icon = request.FILES['icon']

        cat.save()
        messages.success(request, 'Neşir kategoriýasy üstünlikli üýtgedildi!')
        return redirect('panel_library_categories')
    return render(request, 'panel/library_category_form.html', {'action': 'edit', 'obj': cat})


@panel_login_required
def panel_library_category_delete(request, pk):
    cat = get_object_or_404(LibraryCategory, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Kategoriýa öçürildi.')
    return redirect('panel_library_categories')


# ─────────────────────────────────────────────
# LIBRARY BOOKS (ŽURNAL SANLARY / KITAPLAR)
# ─────────────────────────────────────────────

@panel_login_required
def panel_library_books(request):
    if request.method == 'POST' and request.POST.get('action') == 'delete_selected':
        selected_ids = request.POST.getlist('selected_items')
        if selected_ids:
            count = LibraryBook.objects.filter(id__in=selected_ids).delete()[0]
            messages.success(request, f'{count} sany neşir sany üstünlikli pozuldy.')
        return redirect('panel_library_books')

    category_id = request.GET.get('category')
    books = LibraryBook.objects.select_related('category').all().order_by('-year', '-uploaded_at', '-id')
    if category_id:
        books = books.filter(category_id=category_id)

    categories = LibraryCategory.objects.all().order_by('order', 'name_tm')
    return render(request, 'panel/library_books.html', {
        'books': books,
        'categories': categories,
        'selected_category': category_id,
    })


@panel_login_required
def panel_library_book_add(request):
    categories = LibraryCategory.objects.all().order_by('order', 'name_tm')
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        category_id = request.POST.get('category')
        if not category_id:
            default_cat = LibraryCategory.objects.order_by('id').first()
            if not default_cat:
                default_cat = LibraryCategory.objects.create(name_tm="Elektron neşirler")
            category_id = default_cat.id

        if not title_tm:
            messages.error(request, 'Sözbaşy girizmek hökmanydyr!')
            return render(request, 'panel/library_book_form.html', {
                'action': 'add', 'categories': categories, 'post': request.POST
            })

        book = LibraryBook(
            category_id=category_id,
            title_tm=title_tm,
            title_en=request.POST.get('title_en', '').strip(),
            title_ru=request.POST.get('title_ru', '').strip(),
            year=int(request.POST.get('year', 2026) or 2026),
        )
        if 'pdf_file' in request.FILES:
            book.pdf_file = request.FILES['pdf_file']
        if 'image' in request.FILES:
            book.image = request.FILES['image']
        elif 'cover_image' in request.FILES:
            book.cover_image = request.FILES['cover_image']

        if 'image_en' in request.FILES:
            book.image_en = request.FILES['image_en']
        if 'image_ru' in request.FILES:
            book.image_ru = request.FILES['image_ru']

        book.save()
        messages.success(request, 'Neşir üstünlikli goşuldy!')
        return redirect('panel_library_books')
    return render(request, 'panel/library_book_form.html', {'action': 'add', 'categories': categories})


@panel_login_required
def panel_library_book_edit(request, pk):
    book = get_object_or_404(LibraryBook, pk=pk)
    categories = LibraryCategory.objects.all().order_by('order', 'name_tm')
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        category_id = request.POST.get('category')
        if not category_id:
            category_id = book.category_id
            if not category_id:
                default_cat = LibraryCategory.objects.order_by('id').first()
                if not default_cat:
                    default_cat = LibraryCategory.objects.create(name_tm="Elektron neşirler")
                category_id = default_cat.id

        if not title_tm:
            messages.error(request, 'Sözbaşy girizmek hökmanydyr!')
            return render(request, 'panel/library_book_form.html', {
                'action': 'edit', 'obj': book, 'categories': categories
            })

        book.category_id = category_id
        book.title_tm = title_tm
        book.title_en = request.POST.get('title_en', '').strip()
        book.title_ru = request.POST.get('title_ru', '').strip()
        book.year = int(request.POST.get('year', 2026) or 2026)

        if 'pdf_file' in request.FILES:
            book.pdf_file = request.FILES['pdf_file']

        if request.POST.get('clear_image') == '1':
            book.image = None
            book.cover_image = None
        elif 'image' in request.FILES:
            book.image = request.FILES['image']
        elif 'cover_image' in request.FILES:
            book.cover_image = request.FILES['cover_image']

        if request.POST.get('clear_image_en') == '1':
            book.image_en = None
        elif 'image_en' in request.FILES:
            book.image_en = request.FILES['image_en']

        if request.POST.get('clear_image_ru') == '1':
            book.image_ru = None
        elif 'image_ru' in request.FILES:
            book.image_ru = request.FILES['image_ru']

        book.save()

        messages.success(request, 'Neşir sany üstünlikli üýtgedildi!')
        return redirect('panel_library_books')
    return render(request, 'panel/library_book_form.html', {
        'action': 'edit', 'obj': book, 'categories': categories
    })


@panel_login_required
def panel_library_book_delete(request, pk):
    book = get_object_or_404(LibraryBook, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Neşir sany öçürildi.')
    return redirect('panel_library_books')


# ─────────────────────────────────────────────
# LOGS & ANALYTICS (GIRIŞ WE HEREKET LOGLARY)
# ─────────────────────────────────────────────

from django.core.paginator import Paginator


@panel_login_required
def panel_logs(request):
    tab = request.GET.get('tab', 'audit')  # 'audit', 'visitors', 'top'
    q = request.GET.get('q', '').strip()
    action_filter = request.GET.get('action', '').strip()
    module_filter = request.GET.get('module', '').strip()

    # Time-based stats
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_visits = VisitorLog.objects.count()
    today_visits = VisitorLog.objects.filter(timestamp__gte=today_start).count()
    today_unique_ips = VisitorLog.objects.filter(timestamp__gte=today_start).values('ip_address').distinct().count()
    total_actions = AdminAuditLog.objects.count()

    # Top visited pages
    top_pages = VisitorLog.objects.values('path', 'page_title').annotate(
        views_count=Count('id'),
        unique_ips=Count('ip_address', distinct=True)
    ).order_by('-views_count')[:25]

    # Audit Logs Query
    audit_qs = AdminAuditLog.objects.all().order_by('-timestamp')
    if q and tab == 'audit':
        audit_qs = audit_qs.filter(
            Q(user_name__icontains=q) |
            Q(object_repr__icontains=q) |
            Q(details__icontains=q) |
            Q(ip_address__icontains=q)
        )
    if action_filter:
        audit_qs = audit_qs.filter(action=action_filter)
    if module_filter:
        audit_qs = audit_qs.filter(module=module_filter)

    audit_paginator = Paginator(audit_qs, 40)
    audit_page_num = request.GET.get('page', 1)
    audit_page = audit_paginator.get_page(audit_page_num)

    # Visitor Logs Query
    visitor_qs = VisitorLog.objects.all().order_by('-timestamp')
    if q and tab == 'visitors':
        visitor_qs = visitor_qs.filter(
            Q(path__icontains=q) |
            Q(page_title__icontains=q) |
            Q(ip_address__icontains=q) |
            Q(device__icontains=q) |
            Q(user_name__icontains=q)
        )

    visitor_paginator = Paginator(visitor_qs, 40)
    visitor_page_num = request.GET.get('vpage', 1)
    visitor_page = visitor_paginator.get_page(visitor_page_num)

    available_modules = AdminAuditLog.objects.values_list('module', flat=True).distinct()

    return render(request, 'panel/logs.html', {
        'tab': tab,
        'q': q,
        'action_filter': action_filter,
        'module_filter': module_filter,
        'audit_logs': audit_page,
        'visitor_logs': visitor_page,
        'top_pages': top_pages,
        'total_visits': total_visits,
        'today_visits': today_visits,
        'today_unique_ips': today_unique_ips,
        'total_actions': total_actions,
        'available_modules': available_modules,
        'now': now,
    })


@panel_login_required
def panel_logs_clear(request):
    if request.method == 'POST':
        clear_type = request.POST.get('clear_type')
        if clear_type == 'visitors':
            VisitorLog.objects.all().delete()
            log_admin_action(request, 'DELETE', 'Loglar', details="Ähli myhman loglary arassalandy")
            messages.success(request, 'Myhman loglary üstünlikli arassalandy.')
            return redirect(f"{reverse('panel_logs')}?tab=visitors")
        elif clear_type == 'audit':
            AdminAuditLog.objects.all().delete()
            log_admin_action(request, 'DELETE', 'Loglar', details="Admin hereket loglary arassalandy")
            messages.success(request, 'Admin hereket loglary üstünlikli arassalandy.')
            return redirect(f"{reverse('panel_logs')}?tab=audit")
    return redirect('panel_logs')


# ─────────────────────────────────────────────
# SECURITY & IP RESTRICTION (IP RUGSATLARY)
# ─────────────────────────────────────────────

def validate_ip_or_cidr(ip_str):
    """Returns True if string is a valid IPv4/IPv6 or CIDR notation."""
    ip_str = (ip_str or '').strip()
    try:
        if '/' in ip_str:
            ipaddress.ip_network(ip_str, strict=False)
        else:
            ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


@panel_login_required
def panel_allowed_ips(request):
    site_settings = SiteSettings.get_settings()
    current_ip = get_client_ip(request)

    # Ensure hardcoded safe admin IPs exist in database
    default_ips = [
        ('20.20.21.143', 'Esasy Administrator (Siziň Kompýuteriňiz)'),
        ('127.0.0.1', 'Lokal Serwer (Localhost)'),
        ('216.250.9.135', 'Institut Serweri (Public IP 1)'),
        ('216.250.10.252', 'Institut Serweri (Public IP 2)'),
    ]
    for def_ip, def_lbl in default_ips:
        if not AllowedIP.objects.filter(ip_address=def_ip).exists():
            AllowedIP.objects.create(ip_address=def_ip, label=def_lbl, is_active=True)

    if request.method == 'POST' and request.POST.get('action') == 'delete_selected':
        selected_ids = request.POST.getlist('selected_items')
        if selected_ids:
            count = AllowedIP.objects.filter(id__in=selected_ids).delete()[0]
            log_admin_action(request, 'DELETE', 'Howpsuzlyk', details=f"{count} sany IP sanawdan öçürildi")
            messages.success(request, f"{count} sany IP üstünlikli pozuldy.")
        return redirect('panel_allowed_ips')

    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    ips_qs = AllowedIP.objects.all().order_by('-created_at')
    if q:
        ips_qs = ips_qs.filter(Q(ip_address__icontains=q) | Q(label__icontains=q))
    if status_filter == 'active':
        ips_qs = ips_qs.filter(is_active=True)
    elif status_filter == 'inactive':
        ips_qs = ips_qs.filter(is_active=False)

    total_count = AllowedIP.objects.count()
    active_count = AllowedIP.objects.filter(is_active=True).count()

    from .middleware import AdminIPRestrictionMiddleware
    current_ip_whitelisted = AdminIPRestrictionMiddleware.is_ip_allowed(current_ip)

    return render(request, 'panel/allowed_ips.html', {
        'allowed_ips': ips_qs,
        'site_settings': site_settings,
        'current_ip': current_ip,
        'current_ip_whitelisted': current_ip_whitelisted,
        'total_count': total_count,
        'active_count': active_count,
        'q': q,
        'status_filter': status_filter,
    })


@panel_login_required
def panel_allowed_ip_add(request):
    if request.method == 'POST':
        raw_ip = request.POST.get('ip_address', '').strip()
        label = request.POST.get('label', '').strip()
        is_active = request.POST.get('is_active') == '1'

        if not raw_ip:
            messages.error(request, 'IP salgysyny girizmek hökmanydyr!')
            return redirect('panel_allowed_ips')

        if not validate_ip_or_cidr(raw_ip):
            messages.error(request, f'Nädogry IP salgysy: "{raw_ip}". Dogry IPv4, IPv6 ýa-da CIDR formatyny ulanyň (mysal: 192.168.1.50 ýa-da 192.168.1.0/24).')
            return redirect('panel_allowed_ips')

        if AllowedIP.objects.filter(ip_address=raw_ip).exists():
            messages.error(request, f'Bu IP salgysy ("{raw_ip}") eýýäm sanawda bar!')
            return redirect('panel_allowed_ips')

        AllowedIP.objects.create(
            ip_address=raw_ip,
            label=label,
            is_active=is_active
        )
        log_admin_action(request, 'CREATE', 'Howpsuzlyk', object_repr=raw_ip, details=f"Täze IP rugsatlara goşuldy: {raw_ip} ({label or 'Bellik ýok'})")
        messages.success(request, f'IP salgysy ("{raw_ip}") üstünlikli goşuldy!')
    return redirect('panel_allowed_ips')


@panel_login_required
def panel_allowed_ip_add_current(request):
    if request.method == 'POST':
        current_ip = get_client_ip(request)
        if AllowedIP.objects.filter(ip_address=current_ip).exists():
            obj = AllowedIP.objects.get(ip_address=current_ip)
            if not obj.is_active:
                obj.is_active = True
                obj.save()
                messages.success(request, f'Häzirki IP salgyňyz ("{current_ip}") işjeňleşdirildi!')
            else:
                messages.info(request, f'Häzirki IP salgyňyz ("{current_ip}") eýýäm rugsat berlenler sanawynda bar.')
        else:
            AllowedIP.objects.create(
                ip_address=current_ip,
                label="Häzirki enjamym (Administrator)",
                is_active=True
            )
            log_admin_action(request, 'CREATE', 'Howpsuzlyk', object_repr=current_ip, details="Häzirki IP salgysy rugsatlara goşuldy")
            messages.success(request, f'Häzirki IP salgyňyz ("{current_ip}") üstünlikli sanawa goşuldy!')
    return redirect('panel_allowed_ips')


@panel_login_required
def panel_allowed_ips_toggle_global(request):
    if request.method == 'POST':
        site_settings = SiteSettings.get_settings()
        new_state = not site_settings.ip_restriction_enabled

        # Safety check: if enabling, make sure there is at least one active IP, or auto-add current IP
        if new_state:
            active_count = AllowedIP.objects.filter(is_active=True).count()
            if active_count == 0:
                current_ip = get_client_ip(request)
                AllowedIP.objects.create(
                    ip_address=current_ip,
                    label="Administrator (Awtomatiki goşuldy)",
                    is_active=True
                )
                messages.info(request, f'Ulgamdan çykyp galmazlygyňyz üçin häzirki IP salgyňyz ("{current_ip}") awtomatiki sanawa goşuldy.')

        site_settings.ip_restriction_enabled = new_state
        site_settings.save()

        status_text = "Işledildi (Diňe rugsat berlen IP-ler girip biler)" if new_state else "Öçürildi (Ähli IP-ler girip biler)"
        log_admin_action(request, 'UPDATE', 'Howpsuzlyk', details=f"IP çäklendirmesi {status_text}")
        messages.success(request, f"IP çäklendirmesi üstünlikli {status_text}!")
    return redirect('panel_allowed_ips')


@panel_login_required
def panel_allowed_ip_toggle(request, pk):
    ip_obj = get_object_or_404(AllowedIP, pk=pk)
    if request.method == 'POST':
        ip_obj.is_active = not ip_obj.is_active
        ip_obj.save()
        st = "işjeňleşdirildi" if ip_obj.is_active else "öçürildi"
        log_admin_action(request, 'UPDATE', 'Howpsuzlyk', object_repr=ip_obj.ip_address, details=f"IP {ip_obj.ip_address} {st}")
        messages.success(request, f"{ip_obj.ip_address} ýagdaýy {st}.")
    return redirect('panel_allowed_ips')


@panel_login_required
def panel_allowed_ip_edit(request, pk):
    ip_obj = get_object_or_404(AllowedIP, pk=pk)
    if request.method == 'POST':
        raw_ip = request.POST.get('ip_address', '').strip()
        label = request.POST.get('label', '').strip()
        is_active = request.POST.get('is_active') == '1'

        if not raw_ip:
            messages.error(request, 'IP salgysy hökmanydyr!')
            return redirect('panel_allowed_ips')

        if not validate_ip_or_cidr(raw_ip):
            messages.error(request, f'Nädogry IP salgysy: "{raw_ip}".')
            return redirect('panel_allowed_ips')

        existing = AllowedIP.objects.filter(ip_address=raw_ip).exclude(pk=pk)
        if existing.exists():
            messages.error(request, f'Bu IP salgysy ("{raw_ip}") başga bir ýazgyda eýýäm bar!')
            return redirect('panel_allowed_ips')

        ip_obj.ip_address = raw_ip
        ip_obj.label = label
        ip_obj.is_active = is_active
        ip_obj.save()

        log_admin_action(request, 'UPDATE', 'Howpsuzlyk', object_repr=raw_ip, details=f"IP maglumaty üýtgedildi: {raw_ip}")
        messages.success(request, f'IP salgysy ("{raw_ip}") üstünlikli üýtgedildi!')
    return redirect('panel_allowed_ips')


@panel_login_required
def panel_allowed_ip_delete(request, pk):
    ip_obj = get_object_or_404(AllowedIP, pk=pk)
    if request.method == 'POST':
        addr = ip_obj.ip_address
        ip_obj.delete()
        log_admin_action(request, 'DELETE', 'Howpsuzlyk', object_repr=addr, details=f"IP sanawdan öçürildi: {addr}")
        messages.success(request, f'IP salgysy ("{addr}") üstünlikli pozuldy.')
    return redirect('panel_allowed_ips')



