from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Page, SliderImage, News, Faculty, Department, Olympiad, Partner, Document, ContactMessage

def home(request):
    sliders = SliderImage.objects.all()
    news_list = News.objects.all()[:6]
    partners = Partner.objects.all()
    recent_reports = Document.objects.filter(category='Hasabat')[:6]
    
    # Static stats corresponding to TDMai counts
    stats = {
        'books': 45000,
        'majors': 12,
        'teachers': 280,
        'students': 3200
    }
    
    context = {
        'sliders': sliders,
        'news_list': news_list,
        'partners': partners,
        'recent_reports': recent_reports,
        'stats': stats,
        'is_home': True
    }
    return render(request, 'home.html', context)


def news_list(request):
    all_news = News.objects.all()
    context = {
        'all_news': all_news,
        'title': 'Täzelikler'
    }
    return render(request, 'news/list.html', context)


def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    
    # Increment view count
    news_item.views_count += 1
    news_item.save(update_fields=['views_count'])
    
    recent_news = News.objects.exclude(pk=pk)[:5]
    
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
    Valid choices: tm, eng, rus
    """
    lang = request.GET.get('lang', 'tm')
    if lang in ['tm', 'eng', 'rus']:
        request.session['lang'] = lang
        
    # Redirect back to the referrer or homepage
    referrer = request.META.get('HTTP_REFERER', '/')
    return redirect(referrer)


def page_detail(request, slug):
    """
    Renders dynamic hierarchical text pages.
    """
    page = get_object_or_404(Page, slug=slug)
    
    # Get sibling pages for sidebar navigation
    siblings = []
    if page.parent:
        siblings = page.parent.subpages.exclude(pk=page.pk)
    
    context = {
        'page': page,
        'siblings': siblings
    }
    return render(request, 'page_detail.html', context)
