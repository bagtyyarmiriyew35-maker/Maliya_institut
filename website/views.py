from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Page, SliderImage, News, Faculty, Department, Olympiad, Partner, Document, ContactMessage, SiteSettings, LibraryCategory, LibraryBook, BilimNews

def get_recent_contents(limit=10):
    """
    Fetches the 10 latest added contents across the site:
    - Pages from sections (institut and its subpages/sub-subpages, ylym, olimpiada, baslesikler, halkara, dalasgar)
    - Documents (reports, etc.)
    EXCLUDES:
    - News (News, BilimNews)
    - FAQ / Sorag-jogap (section='sorag_jogap')
    """
    pages = list(Page.objects.select_related('parent').exclude(section='sorag_jogap').order_by('-created_at', '-id')[:limit])
    docs = list(Document.objects.all().order_by('-uploaded_at', '-id')[:limit])

    section_icon_map = {
        'institut': 'fa-solid fa-building-columns',
        'ylym': 'fa-solid fa-flask',
        'olimpiada': 'fa-solid fa-award',
        'baslesikler': 'fa-solid fa-trophy',
        'halkara': 'fa-solid fa-earth-americas',
        'dalasgar': 'fa-solid fa-user-graduate',
    }

    section_names = {
        'institut': {'tm': 'Institut', 'en': 'Institute', 'ru': 'Институт'},
        'ylym': {'tm': 'Ylym', 'en': 'Science', 'ru': 'Наука'},
        'olimpiada': {'tm': 'Olimpiadalar', 'en': 'Olympiads', 'ru': 'Олимпиады'},
        'baslesikler': {'tm': 'Bäsleşikler', 'en': 'Contests', 'ru': 'Конкурсы'},
        'halkara': {'tm': 'Halkara hyzmatdaşlyk', 'en': 'International', 'ru': 'Международное'},
        'dalasgar': {'tm': 'Dalaşgär', 'en': 'Applicant', 'ru': 'Абитуриент'},
        'sorag_jogap': {'tm': 'Sorag-jogap', 'en': 'FAQ', 'ru': 'Вопросы и ответы'},
    }

    doc_cat_names = {
        'Kitaphana': {'tm': 'Kitaphana', 'en': 'Library', 'ru': 'Библиотека'},
        'Sanly Bilim': {'tm': 'Sanly Bilim', 'en': 'Digital Education', 'ru': 'Цифровое образование'},
        'Hasabat': {'tm': 'Hepdelik Hasabat', 'en': 'Weekly Report', 'ru': 'Еженедельный отчет'},
        'Maksatnama': {'tm': 'Maksatnamalar', 'en': 'Programs', 'ru': 'Программы'},
    }

    items = []
    for p in pages:
        img_tm = p.image or (p.parent.image if p.parent else None)
        img_en = p.image_en or (p.parent.image_en if p.parent else None) or img_tm
        img_ru = p.image_ru or (p.parent.image_ru if p.parent else None) or img_tm

        if p.parent:
            badge_tm = p.parent.title_tm
            badge_en = p.parent.title_en or p.parent.title_tm
            badge_ru = p.parent.title_ru or p.parent.title_tm
        else:
            s_dict = section_names.get(p.section, {})
            badge_tm = s_dict.get('tm', p.get_section_display_name())
            badge_en = s_dict.get('en', badge_tm)
            badge_ru = s_dict.get('ru', badge_tm)

        icon = section_icon_map.get(p.section, 'fa-solid fa-file-lines')

        items.append({
            'type': 'page',
            'title_tm': p.title_tm,
            'title_en': p.title_en or p.title_tm,
            'title_ru': p.title_ru or p.title_tm,
            'badge': badge_tm,
            'badge_tm': badge_tm,
            'badge_en': badge_en,
            'badge_ru': badge_ru,
            'url': f'/p/{p.slug}/',
            'image': img_tm,
            'image_tm': img_tm,
            'image_en': img_en,
            'image_ru': img_ru,
            'icon': icon,
            'date': getattr(p, 'created_at', None),
            'sort_date': getattr(p, 'created_at', None),
        })

    for d in docs:
        c_dict = doc_cat_names.get(d.category, {})
        d_badge_tm = c_dict.get('tm', d.get_category_display() or 'Resminama')
        d_badge_en = c_dict.get('en', 'Document')
        d_badge_ru = c_dict.get('ru', 'Документ')

        items.append({
            'type': 'document',
            'title_tm': d.title_tm,
            'title_en': d.title_en or d.title_tm,
            'title_ru': d.title_ru or d.title_tm,
            'badge': d_badge_tm,
            'badge_tm': d_badge_tm,
            'badge_en': d_badge_en,
            'badge_ru': d_badge_ru,
            'url': f'/document/{d.pk}/',
            'image': d.image,
            'icon': 'fa-solid fa-file-pdf',
            'date': d.uploaded_at,
            'sort_date': d.uploaded_at,
        })

    items.sort(key=lambda x: (x['sort_date'] is not None, x['sort_date']), reverse=True)
    return items[:limit]


def home(request):
    sliders = SliderImage.objects.all()
    news_list = News.objects.all()[:6]
    partners = Partner.objects.all()
    recent_reports = Document.objects.filter(category='Hasabat')[:6]
    recent_contents = get_recent_contents(limit=10)
    
    # Fetch stats dynamically from SiteSettings
    settings_obj = SiteSettings.get_settings()
    stats = {
        'books': settings_obj.stat_books,
        'majors': settings_obj.stat_majors,
        'teachers': settings_obj.stat_teachers,
        'students': settings_obj.stat_students
    }
    
    library_categories = LibraryCategory.objects.all().order_by('order', 'id')
    featured_category = library_categories.first()
    featured_books = []
    if featured_category:
        featured_books = list(featured_category.books.all().order_by('-uploaded_at', '-id')[:6])
    if not featured_books:
        featured_books = list(LibraryBook.objects.all().order_by('-uploaded_at', '-id')[:6])
    
    # Bilim.tm-den iň soňky 9 sany täzelik
    bilim_news = BilimNews.objects.all().order_by('-published_date', '-id')[:9]

    context = {
        'sliders': sliders,
        'news_list': news_list,
        'bilim_news': bilim_news,
        'partners': partners,
        'recent_reports': recent_reports,
        'recent_contents': recent_contents,
        'library_categories': library_categories,
        'featured_category': featured_category,
        'featured_books': featured_books,
        'stats': stats,
        'is_home': True
    }
    return render(request, 'home.html', context)


def bilim_news_detail(request, pk):
    news_item = get_object_or_404(BilimNews, pk=pk)
    
    viewed_news = request.session.get('viewed_bilim_news', [])
    if pk not in viewed_news:
        news_item.views_count += 1
        news_item.save(update_fields=['views_count'])
        viewed_news.append(pk)
        request.session['viewed_bilim_news'] = viewed_news
        request.session.modified = True
    
    other_news = BilimNews.objects.exclude(pk=pk).order_by('-published_date', '-id')[:6]
    
    context = {
        'news_item': news_item,
        'other_news': other_news
    }
    return render(request, 'news/bilim_detail.html', context)



def news_list(request):
    news_queryset = News.objects.all()
    paginator = Paginator(news_queryset, 6)
    
    page = request.GET.get('page')
    try:
        all_news = paginator.page(page)
    except PageNotAnInteger:
        all_news = paginator.page(1)
    except EmptyPage:
        all_news = paginator.page(paginator.num_pages)

    context = {
        'all_news': all_news,
        'title': 'Täzelikler'
    }
    return render(request, 'news/list.html', context)


def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    
    # Session arkaly diňe bir gezek okaldy diýip hasaba alýarys
    viewed_news = request.session.get('viewed_news', [])
    if pk not in viewed_news:
        news_item.views_count += 1
        news_item.save(update_fields=['views_count'])
        viewed_news.append(pk)
        request.session['viewed_news'] = viewed_news
        request.session.modified = True
    
    recent_news = News.objects.exclude(pk=pk).order_by('-published_date', '-id')[:9]
    
    context = {
        'news_item': news_item,
        'recent_news': recent_news
    }
    return render(request, 'news/detail.html', context)


def faculty_detail(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    context = {
        'faculty': faculty,
        'departments': faculty.departments.all()
    }
    return render(request, 'about/faculty_detail.html', context)


def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    context = {
        'department': department,
        'faculty': department.faculty
    }
    return render(request, 'about/department_detail.html', context)


def olympiads(request):
    all_olympiads = Olympiad.objects.all()
    # Group olympiads by year
    years = sorted(list(set(all_olympiads.values_list('year', flat=True))), reverse=True)
    grouped_olympiads = {}
    for year in years:
        grouped_olympiads[year] = all_olympiads.filter(year=year)
        
    context = {
        'grouped_olympiads': grouped_olympiads,
        'years': years
    }
    return render(request, 'olympiads/list.html', context)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Siziň hatyňyz üstünlikli iberildi! Sag boluň.')
        else:
            messages.error(request, 'Ähli meýdançalary dolduryň.')
        return redirect('contact')
        
    return render(request, 'contact.html')


def set_language(request):
    """
    Switch language code via request parameter.
    Valid choices: tm, eng, rus (also accepts en, ru)
    """
    raw_lang = str(request.GET.get('lang', 'tm')).strip().lower()
    if raw_lang in ['eng', 'en']:
        target_lang = 'eng'
    elif raw_lang in ['rus', 'ru']:
        target_lang = 'rus'
    else:
        target_lang = 'tm'

    request.session['lang'] = target_lang
    request.session.modified = True
        
    # Redirect back to the referrer or homepage
    referrer = request.META.get('HTTP_REFERER') or '/'
    response = redirect(referrer)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response.set_cookie('site_lang', target_lang, max_age=365 * 24 * 60 * 60, path='/', samesite='Lax')
    return response


try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def page_detail(request, slug):
    """
    Renders dynamic hierarchical text pages with PyPDF2 document inspection and continuous rendering.
    """
    page = get_object_or_404(Page, slug=slug)
    
    subpages = page.subpages.all().order_by('order', 'title_tm')
    
    # Get sibling pages for sidebar navigation
    siblings = []
    if page.parent:
        siblings = page.parent.subpages.all().order_by('order', 'title_tm')
    elif subpages.exists():
        siblings = subpages

    pdf_page_count = 0
    if page.pdf_file and PyPDF2 is not None:
        try:
            reader = PyPDF2.PdfReader(page.pdf_file.path)
            pdf_page_count = len(reader.pages)
        except Exception:
            pdf_page_count = 0
    
    context = {
        'page': page,
        'subpages': subpages,
        'siblings': siblings,
        'pdf_page_count': pdf_page_count
    }
    if page.slug == 'hepdelik-sanly-hasabat' or 'hasabat' in page.slug:
        context['weekly_reports'] = Document.objects.filter(category='Hasabat')

    return render(request, 'page_detail.html', context)


def document_detail(request, pk):
    """
    Renders dedicated Document viewer page with PDF.js continuous rendering (inspired by Mejlis Arhiw).
    """
    document = get_object_or_404(Document, pk=pk)
    
    pdf_page_count = 0
    if document.file and document.file.name.lower().endswith('.pdf') and PyPDF2 is not None:
        try:
            reader = PyPDF2.PdfReader(document.file.path)
            pdf_page_count = len(reader.pages)
        except Exception:
            pdf_page_count = 0
            
    recent_documents = Document.objects.filter(category=document.category).exclude(pk=pk).order_by('-uploaded_at')[:9]
    
    context = {
        'document': document,
        'pdf_page_count': pdf_page_count,
        'recent_documents': recent_documents,
    }
    return render(request, 'document_detail.html', context)


def library_list(request):
    """
    Renders all publications or redirects to first category with issues grid.
    """
    first_cat = LibraryCategory.objects.order_by('order', 'id').first()
    if first_cat:
        return redirect('library_detail', pk=first_cat.pk)
    return redirect('home')


def library_detail(request, pk):
    """
    Renders the list of books/issues for a specific LibraryCategory (journal).
    """
    category = get_object_or_404(LibraryCategory, pk=pk)
    books = category.books.all().order_by('id')
    all_categories = LibraryCategory.objects.all().order_by('order', 'id')
    
    context = {
        'category': category,
        'books': books,
        'all_categories': all_categories,
        'title': category.name_tm,
    }
    return render(request, 'library/detail.html', context)


def library_book_detail(request, pk):
    """
    Renders dedicated Journal Book viewer page with PDF.js continuous rendering
    identical to document_detail (Mejlis Arhiw style with header photo).
    """
    book = get_object_or_404(LibraryBook, pk=pk)
    other_books = LibraryBook.objects.filter(category=book.category).exclude(pk=pk).order_by('-year', '-uploaded_at', '-id')[:8]
    
    context = {
        'book': book,
        'other_books': other_books,
        'title': book.title_tm,
    }
    return render(request, 'library/book_detail.html', context)


import os
from django.conf import settings
from django.http import HttpResponse, Http404

def serve_pdf_engine_lib(request):
    """Directly streams PDF.js library via Django to bypass Nginx static buffer limits."""
    candidates = [
        os.path.join(settings.BASE_DIR, 'static', 'js', 'p.js'),
        os.path.join(settings.BASE_DIR, 'static', 'js', 'pdf.min.js'),
        os.path.join(getattr(settings, 'STATIC_ROOT', ''), 'js', 'p.js') if getattr(settings, 'STATIC_ROOT', None) else '',
        os.path.join(getattr(settings, 'STATIC_ROOT', ''), 'js', 'pdf.min.js') if getattr(settings, 'STATIC_ROOT', None) else '',
    ]
    for p in candidates:
        if p and os.path.exists(p):
            with open(p, 'rb') as f:
                content = f.read()
            resp = HttpResponse(content, content_type='application/javascript; charset=utf-8')
            resp['Cache-Control'] = 'public, max-age=31536000'
            return resp
    raise Http404("PDF.js library not found")


def serve_pdf_engine_worker(request):
    """Directly streams PDF.js worker via Django to bypass Nginx static buffer limits."""
    candidates = [
        os.path.join(settings.BASE_DIR, 'static', 'js', 'pw.js'),
        os.path.join(settings.BASE_DIR, 'static', 'js', 'pdf.worker.min.js'),
        os.path.join(getattr(settings, 'STATIC_ROOT', ''), 'js', 'pw.js') if getattr(settings, 'STATIC_ROOT', None) else '',
        os.path.join(getattr(settings, 'STATIC_ROOT', ''), 'js', 'pdf.worker.min.js') if getattr(settings, 'STATIC_ROOT', None) else '',
    ]
    for p in candidates:
        if p and os.path.exists(p):
            with open(p, 'rb') as f:
                content = f.read()
            resp = HttpResponse(content, content_type='application/javascript; charset=utf-8')
            resp['Cache-Control'] = 'public, max-age=31536000'
            return resp
    raise Http404("PDF.js worker not found")



