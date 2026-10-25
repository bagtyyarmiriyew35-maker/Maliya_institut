import os
from django import template
from django.utils.safestring import mark_safe

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
    'news_subtitle': {
        'tm': 'Maliýe institutynyň durmuşyndaky iň täze habarlar we waka-däpler',
        'eng': 'The latest news and events in the life of the Finance Institute',
        'rus': 'Последние новости и события из жизни Финансового института'
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
    },
    'all_news': {
        'tm': 'Hemme täzelikler',
        'eng': 'All news',
        'rus': 'Все новости'
    },
    'back': {
        'tm': 'Yza',
        'eng': 'Back',
        'rus': 'Назад'
    },
    'back_to_home': {
        'tm': 'Baş sahypa dolan',
        'eng': 'Back to home',
        'rus': 'На главную'
    },
    'write_to_us': {
        'tm': 'Hat ýazyň',
        'eng': 'Write to us',
        'rus': 'Напишите нам'
    },
    'contact_for': {
        'tm': 'Habarlaşmak üçin',
        'eng': 'Contact details',
        'rus': 'Для связи'
    },
    'contact_intro': {
        'tm': 'Maliýe instituty bilen habarlaşmak üçin aşakdaky maglumatlary ulanyp bilersiňiz ýa-da göni hat iberip bilersiňiz.',
        'eng': 'To contact the Finance Institute, you can use the information below or send a message directly.',
        'rus': 'Для связи с Финансовым институтом вы можете воспользоваться контактной информацией ниже или отправить сообщение напрямую.'
    },
    'no_data': {
        'tm': 'Häzirki wagtda maglumat ýok.',
        'eng': 'No information available at the moment.',
        'rus': 'В настоящее время информация отсутствует.'
    },
    'download': {
        'tm': 'Ýükle',
        'eng': 'Download',
        'rus': 'Скачать'
    },
    'read': {
        'tm': 'Okamak',
        'eng': 'Read',
        'rus': 'Читать'
    },
    'open': {
        'tm': 'Aç',
        'eng': 'Open',
        'rus': 'Открыть'
    },
    'all': {
        'tm': 'Ählisi',
        'eng': 'All',
        'rus': 'Все'
    },
    'view_all': {
        'tm': 'Ählisini görkez',
        'eng': 'View all',
        'rus': 'Смотреть все'
    },
    'publications': {
        'tm': 'Elektron neşirler',
        'eng': 'Electronic Publications',
        'rus': 'Электронные издания'
    },
    'publications_journals': {
        'tm': 'Elektron neşirler',
        'eng': 'Publications',
        'rus': 'Публикации'
    },
    'footer_desc': {
        'tm': 'Türkmenistanyň ykdysady we maliýe pudaklary üçin ýokary derejeli hünärmenleri taýýarlaýan öňdebaryjy ýokary okuw mekdebi.',
        'eng': 'A leading higher educational institution training highly qualified specialists for the economic and financial sectors of Turkmenistan.',
        'rus': 'Ведущее высшее учебное заведение, готовящее высококвалифицированных специалистов для экономической и финансовой сфер Туркменистана.'
    },
    'institute_name': {
        'tm': 'Türkmen Döwlet Maliýe Instituty',
        'eng': 'Turkmen State Finance Institute',
        'rus': 'Туркменский государственный финансовый институт'
    },
    'source': {
        'tm': 'Çeşme',
        'eng': 'Source',
        'rus': 'Источник'
    },
    'original_source': {
        'tm': 'Habaryň asyl çeşmesi',
        'eng': 'Original Source',
        'rus': 'Первоисточник'
    },
    'read_on_source': {
        'tm': 'Çeşmesinden okaň',
        'eng': 'Read on source',
        'rus': 'Читать в источнике'
    },
    'source_note': {
        'tm': 'Bu maglumat asyl çeşmesinden alnan bolup, ony çeşmäniň öz sahypasyndan hem okap bilersiňiz.',
        'eng': 'This information is obtained from the original source; you can also read it directly on the source website.',
        'rus': 'Эта информация взята из первоисточника; вы также можете прочитать её непосредственно на сайте источника.'
    },
    'views': {
        'tm': 'gezek görüldi',
        'eng': 'views',
        'rus': 'просмотров'
    },
    'download_pdf': {
        'tm': 'PDF ýükle',
        'eng': 'Download PDF',
        'rus': 'Скачать PDF'
    },
    'pdf_document': {
        'tm': 'PDF resminama',
        'eng': 'PDF Document',
        'rus': 'PDF документ'
    },
    'file_size': {
        'tm': 'Faýlyň göwrümi',
        'eng': 'File size',
        'rus': 'Размер файла'
    }
}

@register.simple_tag
def ui_label(key, lang):
    """
    Renders UI labels in the correct language.
    Usage: {% ui_label 'home' current_lang %}
    """
    lang_code = str(lang or 'tm').strip().lower()
    if 'eng' in lang_code or lang_code == 'en':
        target_lang = 'eng'
    elif 'rus' in lang_code or lang_code == 'ru':
        target_lang = 'rus'
    else:
        target_lang = 'tm'

    if key == 'news_subtitle':
        try:
            from website.models import SiteSettings
            s = SiteSettings.get_settings()
            sub = s.get_news_subtitle(target_lang)
            if sub:
                return sub
        except Exception:
            pass

    if key == 'news':
        try:
            from website.models import SiteSettings
            s = SiteSettings.get_settings()
            title = s.get_news_title(target_lang)
            if title:
                return title
        except Exception:
            pass

    label_dict = UI_VOCABULARY.get(key, {})
    return label_dict.get(target_lang, label_dict.get('tm', key))

@register.simple_tag
def render_lang(obj, field_base, lang):
    """
    Renders the correct translated field from a model instance or dict.
    Usage: {% render_lang faculty 'name' current_lang %}
    Falls back gracefully: selected language -> Turkmen (_tm) -> empty string
    """
    if not obj:
        return ""

    lang_code = str(lang or 'tm').strip().lower()
    if 'eng' in lang_code or lang_code == 'en':
        lang_suffix = 'en'
    elif 'rus' in lang_code or lang_code == 'ru':
        lang_suffix = 'ru'
    else:
        lang_suffix = 'tm'

    if field_base == 'image':
        lang_code = str(lang or 'tm').strip().lower()
        if hasattr(obj, 'get_image'):
            img = obj.get_image(lang_code)
            return img.url if img else ""
        if isinstance(obj, dict):
            return obj.get(f"image_{lang_suffix}") or obj.get("image_tm") or obj.get("image") or ""
        if ('eng' in lang_code or lang_code == 'en') and getattr(obj, 'image_en', None):
            return obj.image_en.url
        if ('rus' in lang_code or lang_code == 'ru') and getattr(obj, 'image_ru', None):
            return obj.image_ru.url
        img = getattr(obj, 'image', None)
        return img.url if img else ""

    attr_name = f"{field_base}_{lang_suffix}"

    val = None
    if isinstance(obj, dict):
        val = obj.get(attr_name)
        if val is not None and isinstance(val, str):
            val = val.strip()
        if not val:
            val = obj.get(f"{field_base}_tm", "")
    else:
        val = getattr(obj, attr_name, None)
        if val is not None and isinstance(val, str):
            val = val.strip()
        if not val:
            val = getattr(obj, f"{field_base}_tm", "")

    # HTML içerik (TinyMCE) üçin mark_safe ulanýarys
    if val and '<' in str(val):
        return mark_safe(val)
    return val or ""


@register.simple_tag
def render_multilingual_image(obj, current_lang='tm'):
    """
    Returns the appropriate ImageField file object for the current language.
    Supports both model instances and dictionary objects.
    Usage: {% render_multilingual_image obj current_lang as current_img %}
    """
    if not obj:
        return None
    lang = str(current_lang or 'tm').lower()
    is_en = ('eng' in lang or lang == 'en')
    is_ru = ('rus' in lang or lang == 'ru')

    if isinstance(obj, dict):
        if is_en and obj.get('image_en'):
            return obj['image_en']
        if is_ru and obj.get('image_ru'):
            return obj['image_ru']
        return obj.get('image') or obj.get('image_tm')

    if hasattr(obj, 'get_image'):
        return obj.get_image(current_lang)

    if is_en and getattr(obj, 'image_en', None):
        return obj.image_en
    if is_ru and getattr(obj, 'image_ru', None):
        return obj.image_ru
    return getattr(obj, 'image', None)

@register.filter
def get_dict_item(dictionary, key):
    """
    Allows dictionary lookup in templates using variable keys.
    Usage: {{ stats|get_dict_item:key_var }}
    """
    if not dictionary:
        return ""
    return dictionary.get(key, "")

import html
from django.utils.html import strip_tags

@register.filter
def clean_excerpt(val, num_words=20):
    """
    Strips HTML tags, decodes HTML entities (&uuml;, &ccedil;, &Yacute;, etc.)
    and truncates text cleanly to num_words.
    """
    if not val:
        return ""
    text = html.unescape(str(val))
    text = strip_tags(text)
    text = html.unescape(text).strip()
    words = text.split()
    if len(words) > num_words:
        return " ".join(words[:num_words]) + "..."
    return text


@register.simple_tag(takes_context=True)
def lang_switch_url(context, lang_code):
    """
    Builds the current page URL with the given lang parameter.
    Preserves all existing query params and replaces or appends ?lang=<code>.
    """
    request = context.get('request')
    if not request:
        return f"?lang={lang_code}"
    query = request.GET.copy()
    query['lang'] = lang_code
    return mark_safe(f"{request.path}?{query.urlencode()}")


@register.simple_tag
def render_source_name(obj, current_lang='tm'):
    """
    Renders the multilingual source name for an object (News or Page).
    Falls back gracefully: selected language -> Turkmen (_tm) -> main -> domain from URL.
    Usage: {% render_source_name news_item current_lang %}
    """
    if not obj:
        return ""
    if hasattr(obj, 'get_source_name'):
        return obj.get_source_name(current_lang)
    return getattr(obj, 'display_source_name', '')


@register.simple_tag
def render_pdf_title(obj, current_lang='tm'):
    """
    Renders the multilingual PDF title for an object (Page, News, BilimNews).
    If custom PDF title is set for the active language, uses it.
    Otherwise, automatically falls back to the object's title in that language.
    Usage: {% render_pdf_title page current_lang %}
    """
    if not obj:
        return ""
    if hasattr(obj, 'get_pdf_title'):
        return obj.get_pdf_title(current_lang)

    l = str(current_lang or 'tm').lower()
    if ('eng' in l or l == 'en'):
        return getattr(obj, 'pdf_title_en', '') or getattr(obj, 'title_en', '') or getattr(obj, 'title_tm', '') or str(obj)
    if ('rus' in l or l == 'ru'):
        return getattr(obj, 'pdf_title_ru', '') or getattr(obj, 'title_ru', '') or getattr(obj, 'title_tm', '') or str(obj)
    return getattr(obj, 'pdf_title_tm', '') or getattr(obj, 'title_tm', '') or str(obj)


@register.filter
def visible_in_lang(pages, lang='tm'):
    """
    Filter an iterable/queryset of Page objects based on active language visibility (TM, EN, RU).
    Usage: {% for sub in p_page.subpages.all|visible_in_lang:current_lang %}
    """
    if not pages:
        return []
    l = str(lang or 'tm').lower()
    if 'eng' in l or l == 'en':
        return [p for p in pages if getattr(p, 'show_in_en', True)]
    elif 'rus' in l or l == 'ru':
        return [p for p in pages if getattr(p, 'show_in_ru', True)]
    else:
        return [p for p in pages if getattr(p, 'show_in_tm', True)]


@register.filter
def is_visible_in(page, lang='tm'):
    """
    Check if a single Page object is visible in the given language.
    Usage: {% if p_page|is_visible_in:current_lang %}
    """
    if not page:
        return True
    l = str(lang or 'tm').lower()
    if 'eng' in l or l == 'en':
        return getattr(page, 'show_in_en', True)
    elif 'rus' in l or l == 'ru':
        return getattr(page, 'show_in_ru', True)
    else:
        return getattr(page, 'show_in_tm', True)


@register.filter
def file_ext(file_field_or_url):
    """Returns lowercased extension without dot (e.g. 'mp4', 'pdf', 'xlsx')."""
    if not file_field_or_url:
        return ''
    try:
        url_or_name = getattr(file_field_or_url, 'name', '') or str(file_field_or_url)
        url_or_name = url_or_name.split('?')[0]
        ext = os.path.splitext(url_or_name)[1].lower().lstrip('.')
        return ext
    except Exception:
        return ''


@register.filter
def file_category(file_field_or_url):
    """
    Returns file category: 'video', 'image', 'audio', 'pdf', 'word', 'excel', 'powerpoint', 'archive', 'text', 'other'
    """
    ext = file_ext(file_field_or_url)
    if ext in ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', 'm4v', '3gp']:
        return 'video'
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico', 'tiff', 'jfif']:
        return 'image'
    if ext in ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'wma', 'opus', 'mid', 'midi']:
        return 'audio'
    if ext == 'pdf':
        return 'pdf'
    if ext in ['doc', 'docx', 'rtf', 'odt']:
        return 'word'
    if ext in ['xls', 'xlsx', 'csv', 'ods', 'xlsm']:
        return 'excel'
    if ext in ['ppt', 'pptx', 'odp', 'pps', 'ppsx']:
        return 'powerpoint'
    if ext in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
        return 'archive'
    if ext in ['txt', 'log', 'md']:
        return 'text'
    return 'other'


@register.filter
def file_icon(file_field_or_url):
    """Returns FontAwesome icon class for the file."""
    cat = file_category(file_field_or_url)
    icons = {
        'video': 'fa-solid fa-file-video',
        'image': 'fa-solid fa-file-image',
        'audio': 'fa-solid fa-file-audio',
        'pdf': 'fa-solid fa-file-pdf',
        'word': 'fa-solid fa-file-word',
        'excel': 'fa-solid fa-file-excel',
        'powerpoint': 'fa-solid fa-file-powerpoint',
        'archive': 'fa-solid fa-file-zipper',
        'text': 'fa-solid fa-file-lines',
        'other': 'fa-solid fa-file',
    }
    return icons.get(cat, 'fa-solid fa-file')


@register.filter
def file_color(file_field_or_url):
    """Returns accent hex color for the file category."""
    cat = file_category(file_field_or_url)
    colors = {
        'video': '#8b5cf6',      # Violet / Modern video purple
        'image': '#0284c7',      # Sky Blue
        'audio': '#e11d48',      # Rose / Vibrant audio
        'pdf': '#ef4444',        # Red
        'word': '#2563eb',       # Blue
        'excel': '#16a34a',      # Green
        'powerpoint': '#ea580c', # Orange
        'archive': '#9333ea',    # Purple
        'text': '#64748b',       # Slate
        'other': '#64748b',
    }
    return colors.get(cat, '#64748b')


@register.filter
def file_bg_color(file_field_or_url):
    """Returns light background hex color for the file category icon box."""
    cat = file_category(file_field_or_url)
    bgs = {
        'video': '#f3e8ff',
        'image': '#e0f2fe',
        'audio': '#ffe4e6',
        'pdf': '#fef2f2',
        'word': '#eff6ff',
        'excel': '#f0fdf4',
        'powerpoint': '#fff7ed',
        'archive': '#faf5ff',
        'text': '#f8fafc',
        'other': '#f8fafc',
    }
    return bgs.get(cat, '#f8fafc')


@register.simple_tag
def file_category_label(file_field_or_url, lang='tm'):
    """Returns localized category badge/name."""
    cat = file_category(file_field_or_url)
    ext = file_ext(file_field_or_url).upper()
    l = str(lang or 'tm').lower()
    is_en = ('eng' in l or l == 'en')
    is_ru = ('rus' in l or l == 'ru')

    labels = {
        'video': ('Wideo faýl' if not is_en and not is_ru else ('Video File' if is_en else 'Видео файл')),
        'image': ('Surat' if not is_en and not is_ru else ('Image / Photo' if is_en else 'Изображение / Фото')),
        'audio': ('Aýdym / Ses' if not is_en and not is_ru else ('Audio File' if is_en else 'Аудиозапись')),
        'pdf': ('PDF Resminama' if not is_en and not is_ru else ('PDF Document' if is_en else 'PDF документ')),
        'word': ('Word Resminama' if not is_en and not is_ru else ('Word Document' if is_en else 'Документ Word')),
        'excel': ('Excel Tablisa' if not is_en and not is_ru else ('Excel Spreadsheet' if is_en else 'Таблица Excel')),
        'powerpoint': ('Prezentasiýa' if not is_en and not is_ru else ('Presentation' if is_en else 'Презентация')),
        'archive': ('Arhiw (Zip/Rar)' if not is_en and not is_ru else ('Archive (Zip/Rar)' if is_en else 'Архив (Zip/Rar)')),
        'text': ('Tekst faýl' if not is_en and not is_ru else ('Text file' if is_en else 'Текстовый файл')),
        'other': (f'{ext} Faýly' if ext else ('Faýl' if not is_en and not is_ru else ('File' if is_en else 'Файл'))),
    }
    return labels.get(cat, 'Faýl')




