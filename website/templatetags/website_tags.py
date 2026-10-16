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
        'tm': 'Elektron neşirler we žurnallar',
        'eng': 'Publications & Journals',
        'rus': 'Электронные издания и журналы'
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
    'views': {
        'tm': 'gezek görüldi',
        'eng': 'views',
        'rus': 'просмотров'
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

