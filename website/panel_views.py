"""
Custom Admin Panel Views — /panel/
All views require staff login. Django's /admin/ remains untouched.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils.text import slugify

from .models import (
    Page, SliderImage, News, Faculty, Department,
    Olympiad, Partner, Document, ContactMessage, SiteSettings,
    LibraryCategory, LibraryBook, BilimNews
)
from .bilim_scraper import sync_bilim_news



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
# Decorator helper — require staff login
# ─────────────────────────────────────────────

def panel_login_required(view_func):
    """Redirect to panel login if not authenticated."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('panel_login')
        return view_func(request, *args, **kwargs)
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
            return redirect('panel_dashboard')
        else:
            error = 'Ulanyjy ady ýa-da açar sözi nädogry!'

    return render(request, 'panel/login.html', {'error': error})


def panel_logout(request):
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

@panel_login_required
def panel_news(request):
    all_news = News.objects.order_by('-published_date')
    return render(request, 'panel/news.html', {'all_news': all_news})


@panel_login_required
def panel_news_add(request):
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        content_tm = request.POST.get('content_tm', '').strip()
        if not title_tm or not content_tm:
            messages.error(request, 'Türkmençe at we mazmun hökmanydyr!')
            return render(request, 'panel/news_form.html', {'action': 'add', 'post': request.POST})
        news = News(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', ''),
            title_ru=request.POST.get('title_ru', ''),
            content_tm=content_tm,
            content_en=request.POST.get('content_en', ''),
            content_ru=request.POST.get('content_ru', ''),
            video_url=request.POST.get('video_url', '').strip(),
        )
        if 'image' in request.FILES:
            news.image = request.FILES['image']
        if 'video' in request.FILES:
            news.video = request.FILES['video']
        news.save()
        messages.success(request, 'Täzelik üstünlikli goşuldy!')
        return redirect('panel_news')
    return render(request, 'panel/news_form.html', {'action': 'add'})


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
        
        if 'image' in request.FILES:
            news.image = request.FILES['image']
        elif 'clear_image' in request.POST:
            news.image = None

        if 'video' in request.FILES:
            news.video = request.FILES['video']
        elif 'clear_video' in request.POST:
            news.video = None

        news.save()
        messages.success(request, 'Täzelik üstünlikli üýtgedildi!')
        return redirect('panel_news')
    return render(request, 'panel/news_form.html', {'action': 'edit', 'obj': news})


@panel_login_required
def panel_news_delete(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news.delete()
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
    if section_code:
        qs = Page.objects.filter(section=section_code)
    else:
        qs = Page.objects.all()

    all_pages = list(qs.select_related('parent').prefetch_related('subpages').order_by('order', 'title_tm'))

    root_section_page = next((p for p in all_pages if p.parent is None), None)

    if root_section_page:
        top_pages = [p for p in all_pages if p != root_section_page and (p.parent_id == root_section_page.pk or p.parent_id is None)]
    else:
        top_pages = [p for p in all_pages if p.parent_id is None]

    # Eger hiç hili top_pages tapylmasa, ähli sahypalary görkez
    if not top_pages:
        top_pages = all_pages

    cards = []

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
    }

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
            pages = Page.objects.filter(section=section, parent__parent=None).exclude(subpages__isnull=False).order_by('order', 'title_tm')
            category_title = f"{section_label} Sahypalary"
        else:
            active_parent = get_object_or_404(Page, pk=parent_param)
            pages = Page.objects.filter(section=section, parent=active_parent).order_by('order', 'title_tm')
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
        page = Page(
            title_tm=title_tm,
            title_en=request.POST.get('title_en', ''),
            title_ru=request.POST.get('title_ru', ''),
            slug=slug,
            section=section,
            content_tm=request.POST.get('content_tm', ''),
            content_en=request.POST.get('content_en', ''),
            content_ru=request.POST.get('content_ru', ''),
            parent=parent,
            order=int(request.POST.get('order', 0) or 0),
        )
        if 'image' in request.FILES:
            page.image = request.FILES['image']
        if 'pdf_file' in request.FILES:
            page.pdf_file = request.FILES['pdf_file']
        page.save()
        messages.success(request, 'Sahypa üstünlikli goşuldy!')
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
        if page.parent is not None:
            parent_id = request.POST.get('parent')
            if parent_id:
                page.parent = Page.objects.filter(pk=parent_id).first()
        page.order = int(request.POST.get('order', 0) or 0)
        if 'image' in request.FILES:
            page.image = request.FILES['image']
        elif request.POST.get('clear_image') == '1':
            page.image = None

        if 'pdf_file' in request.FILES:
            page.pdf_file = request.FILES['pdf_file']
        elif request.POST.get('clear_pdf_file') == '1':
            page.pdf_file = None

        page.save()
        messages.success(request, 'Sahypa üstünlikli üýtgedildi!')
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
    if request.method == 'POST':
        page.delete()
        messages.success(request, 'Sahypa öçürildi.')
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
        faculty.save()
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
        faculty.save()
        messages.success(request, 'Fakultet üstünlikli üýtgedildi!')
        return redirect('panel_faculties')
    return render(request, 'panel/faculty_form.html', {'action': 'edit', 'obj': faculty})


@panel_login_required
def panel_faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        faculty.delete()
        messages.success(request, 'Fakultet öçürildi.')
    return redirect('panel_faculties')


# ─────────────────────────────────────────────
# DEPARTMENTS
# ─────────────────────────────────────────────

@panel_login_required
def panel_departments(request):
    departments = Department.objects.select_related('faculty').order_by('faculty__name_tm', 'name_tm')
    faculties = Faculty.objects.all()
    return render(request, 'panel/departments.html', {'departments': departments, 'faculties': faculties})


@panel_login_required
def panel_department_add(request):
    faculties = Faculty.objects.all()
    if request.method == 'POST':
        name_tm = request.POST.get('name_tm', '').strip()
        description_tm = request.POST.get('description_tm', '').strip()
        faculty_id = request.POST.get('faculty')
        if not name_tm or not description_tm or not faculty_id:
            messages.error(request, 'At, beýan we fakultet hökmanydyr!')
            return render(request, 'panel/department_form.html', {'action': 'add', 'faculties': faculties, 'post': request.POST})
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
        dept.save()
        messages.success(request, 'Kafedra üstünlikli goşuldy!')
        return redirect('panel_departments')
    return render(request, 'panel/department_form.html', {'action': 'add', 'faculties': faculties})


@panel_login_required
def panel_department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    faculties = Faculty.objects.all()
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
        dept.save()
        messages.success(request, 'Kafedra üstünlikli üýtgedildi!')
        return redirect('panel_departments')
    return render(request, 'panel/department_form.html', {'action': 'edit', 'obj': dept, 'faculties': faculties})


@panel_login_required
def panel_department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Kafedra öçürildi.')
    return redirect('panel_departments')


# ─────────────────────────────────────────────
# DOCUMENTS
# ─────────────────────────────────────────────

@panel_login_required
def panel_documents(request):
    category = request.GET.get('category', '')
    docs = Document.objects.order_by('-uploaded_at')
    if category:
        docs = docs.filter(category=category)
    return render(request, 'panel/documents.html', {
        'docs': docs,
        'categories': Document.CATEGORY_CHOICES,
        'selected_category': category,
    })


@panel_login_required
def panel_document_add(request):
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        category = request.POST.get('category', '')
        if not title_tm or not category or 'file' not in request.FILES:
            messages.error(request, 'At, kategoriýa we faýl hökmanydyr!')
            return render(request, 'panel/document_form.html', {
                'categories': Document.CATEGORY_CHOICES, 'post': request.POST, 'action': 'add'
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
        doc.save()
        messages.success(request, 'Resminama üstünlikli goşuldy!')
        return redirect('panel_documents')
    return render(request, 'panel/document_form.html', {'categories': Document.CATEGORY_CHOICES, 'action': 'add'})


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
        doc.save()
        messages.success(request, 'Resminama üstünlikli üýtgedildi!')
        return redirect('panel_documents')
    return render(request, 'panel/document_form.html', {'categories': Document.CATEGORY_CHOICES, 'obj': doc, 'action': 'edit'})


@panel_login_required
def panel_document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        doc.delete()
        messages.success(request, 'Resminama öçürildi.')
    return redirect('panel_documents')


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
        site_settings.email = request.POST.get('email', '')
        site_settings.facebook_url = request.POST.get('facebook_url', '')
        site_settings.twitter_url = request.POST.get('twitter_url', '')
        site_settings.linkedin_url = request.POST.get('linkedin_url', '')
        site_settings.instagram_url = request.POST.get('instagram_url', '')
        site_settings.youtube_url = request.POST.get('youtube_url', '')
        if 'stats_bg_image' in request.FILES:
            site_settings.stats_bg_image = request.FILES['stats_bg_image']
        site_settings.save()
        messages.success(request, 'Sazlamalar üstünlikli ýatyryldy!')
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
        if not title_tm or not category_id:
            messages.error(request, 'Sözbaşy we kategoriýa saýlamak hökmanydyr!')
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

        book.save()
        messages.success(request, 'Neşir sany üstünlikli goşuldy!')
        return redirect('panel_library_books')
    return render(request, 'panel/library_book_form.html', {'action': 'add', 'categories': categories})


@panel_login_required
def panel_library_book_edit(request, pk):
    book = get_object_or_404(LibraryBook, pk=pk)
    categories = LibraryCategory.objects.all().order_by('order', 'name_tm')
    if request.method == 'POST':
        title_tm = request.POST.get('title_tm', '').strip()
        category_id = request.POST.get('category')
        if not title_tm or not category_id:
            messages.error(request, 'Sözbaşy we kategoriýa saýlamak hökmanydyr!')
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

