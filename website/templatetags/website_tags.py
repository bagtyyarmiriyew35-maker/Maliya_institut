from django import template

register = template.Library()

# UI Translation Vocabulary
UI_VOCABULARY = {
    'home': {
        'tm': 'Baş sahypa',
        'eng': 'Home',
        'rus': 'Главная'
    },
    'about': {
        'tm': 'Institut',
        'eng': 'About',
        'rus': 'Институт'
    },
    'history': {
        'tm': 'Taryhy',
        'eng': 'History',
        'rus': 'История'
    },
    'faculties': {
        'tm': 'Fakultetler',
        'eng': 'Faculties',
        'rus': 'Факультеты'
    },
    'departments': {
        'tm': 'Kafedralar',
        'eng': 'Departments',
        'rus': 'Кафедры'
    },
    'olympiads': {
        'tm': 'Olimpiadalar',
        'eng': 'Olympiads',
        'rus': 'Олимпиады'
    },
    'news': {
        'tm': 'Täzelikler',
        'eng': 'News',
        'rus': 'Новости'
    },
    'contact': {
        'tm': 'Habarlaşmak',
        'eng': 'Contact',
        'rus': 'Контакты'
    },
    'login': {
        'tm': 'Ulgama gir',
        'eng': 'Login',
        'rus': 'Войти'
    },
    'address': {
        'tm': 'Salgymyz',
        'eng': 'Address',
        'rus': 'Адрес'
    },
    'phone': {
        'tm': 'Telefon belgiler',
        'eng': 'Phone',
        'rus': 'Телефон'
    },
    'email': {
        'tm': 'Email',
        'eng': 'Email',
        'rus': 'Email'
    },
    'more': {
        'tm': 'Dowamy',
        'eng': 'More',
        'rus': 'Подробнее'
    },
    'all_rights_reserved': {
        'tm': 'Hemme hukuklary goralan',
        'eng': 'All rights reserved',
        'rus': 'Все права защищены'
    },
    'partners': {
        'tm': 'Daşary ýurt hyzmatdaşlarymyz',
        'eng': 'Our International Partners',
        'rus': 'Наши международные партнеры'
    },
    'latest_reports': {
        'tm': 'Soňky goşulan maglumatlar',
        'eng': 'Recently Added Documents',
        'rus': 'Последние добавленные материалы'
    },
    'send': {
        'tm': 'Iber',
        'eng': 'Send',
        'rus': 'Отправить'
    },
    'name': {
        'tm': 'Adyňyz',
        'eng': 'Your Name',
        'rus': 'Ваше имя'
    },
    'subject': {
        'tm': 'Tema',
        'eng': 'Subject',
        'rus': 'Тема'
    },
    'message': {
        'tm': 'Hatyňyz',
        'eng': 'Message',
        'rus': 'Сообщение'
    },
    'books_count': {
        'tm': 'Kitaplaryň sany',
        'eng': 'Books count',
        'rus': 'Количество книг'
    },
    'majors_count': {
        'tm': 'Hünär sany',
        'eng': 'Majors count',
        'rus': 'Специальности'
    },
    'teachers_count': {
        'tm': 'Mugallym sany',
        'eng': 'Teachers count',
        'rus': 'Преподаватели'
    },
    'students_count': {
        'tm': 'Talyp sany',
        'eng': 'Students count',
        'rus': 'Студенты'
    },
    'dean': {
        'tm': 'Dekan',
        'eng': 'Dean',
        'rus': 'Декан'
    },
    'head': {
        'tm': 'Kafedra müdiri',
        'eng': 'Head of Department',
        'rus': 'Заведующий кафедрой'
    },
    'faculty_label': {
        'tm': 'Fakultet',
        'eng': 'Faculty',
        'rus': 'Факультет'
    },
    'back_to_news': {
        'tm': 'Täzeliklere dolanmak',
        'eng': 'Back to news',
        'rus': 'Назад к новостям'
    },
    'recent_news': {
        'tm': 'Soňky täzelikler',
        'eng': 'Recent news',
        'rus': 'Последние новости'
    },
    'weekly_reports': {
        'tm': 'Hepdelik sanly hasabat',
        'eng': 'Weekly digital reports',
        'rus': 'Еженедельные цифровые отчеты'
    }
}

@register.simple_tag
def ui_label(key, lang):
    """
    Renders UI labels in the correct language.
    Usage: {% ui_label 'home' current_lang %}
    """
    lang = lang if lang in ['tm', 'eng', 'rus'] else 'tm'
    label_dict = UI_VOCABULARY.get(key, {})
    return label_dict.get(lang, key)

@register.simple_tag
def render_lang(obj, field_base, lang):
    """
    Renders the correct translated field from a model instance.
    Usage: {% render_lang faculty 'name' current_lang %}
    """
    if not obj:
        return ""
        
    lang_suffix = 'tm'
    if lang == 'eng':
        lang_suffix = 'en'
    elif lang == 'rus':
        lang_suffix = 'ru'
        
    attr_name = f"{field_base}_{lang_suffix}"
    
    val = getattr(obj, attr_name, None)
    if val is None or val == "":
        val = getattr(obj, f"{field_base}_tm", "")
        
    return val

@register.filter
def get_dict_item(dictionary, key):
    """
    Allows dictionary lookup in templates using variable keys.
    Usage: {{ stats|get_dict_item:key_var }}
    """
    if not dictionary:
        return ""
    return dictionary.get(key, "")
