from website.models import Faculty, Page, SiteSettings, ContactMessage, Document

def language_processor(request):
    """
    Context processor to make the current selected language, 
    the list of faculties, the page menu hierarchy, site settings,
    and admin panel unread messages count available globally in templates.
    """
    get_lang = request.GET.get('lang')
    if get_lang:
        candidate = str(get_lang).strip().lower()
        if candidate in ['eng', 'en']:
            lang = 'eng'
        elif candidate in ['rus', 'ru']:
            lang = 'rus'
        else:
            lang = 'tm'
        request.session['lang'] = lang
        request.session.modified = True
    else:
        raw_lang = request.session.get('lang') or request.COOKIES.get('site_lang') or 'tm'
        raw_lang = str(raw_lang).strip().lower()
        if raw_lang in ['eng', 'en']:
            lang = 'eng'
        elif raw_lang in ['rus', 'ru']:
            lang = 'rus'
        else:
            lang = 'tm'
        
    faculties_menu = Faculty.objects.all()
    menu_pages = Page.objects.filter(parent=None).prefetch_related('subpages__subpages')
    weekly_reports_menu = Document.objects.filter(category='Hasabat').order_by('-uploaded_at')[:10]
    site_settings = SiteSettings.get_settings()
    
    # For the custom admin panel sidebar unread counter
    unread_count = 0
    if request.path.startswith('/panel/'):
        unread_count = ContactMessage.objects.filter(is_read=False).count()
    
    return {
        'current_lang': lang,
        'faculties_menu': faculties_menu,
        'menu_pages': menu_pages,
        'weekly_reports_menu': weekly_reports_menu,
        'site_settings': site_settings,
        'unread_count': unread_count,
        'post': {},
    }

