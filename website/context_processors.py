from website.models import Faculty, Page

def language_processor(request):
    """
    Context processor to make the current selected language, 
    the list of faculties, and the page menu hierarchy available globally in templates.
    """
    lang = request.session.get('lang', 'tm')
    if lang not in ['tm', 'eng', 'rus']:
        lang = 'tm'
        
    faculties_menu = Faculty.objects.all()
    menu_pages = Page.objects.filter(parent=None).prefetch_related('subpages')
    
    return {
        'current_lang': lang,
        'faculties_menu': faculties_menu,
        'menu_pages': menu_pages,
    }
