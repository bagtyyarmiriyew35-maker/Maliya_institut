from django.db import models
from django.utils import timezone

class Page(models.Model):
    SECTION_CHOICES = [
        ('institut', 'Institut'),
        ('ylym', 'Ylym'),
        ('baslesikler', 'Bäsleşikler'),
        ('halkara', 'Halkara hyzmatdaşlyk'),
        ('dalasgar', 'Dalaşgär'),
        ('sorag_jogap', 'Sorag-jogap'),
        ('olimpiada', 'Olimpiadalar'),
    ]

    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    section = models.CharField(
        max_length=30,
        choices=SECTION_CHOICES,
        default='institut',
        verbose_name="Bölüm (Section)"
    )
    
    content_tm = models.TextField(blank=True, verbose_name="Content (Turkmen)")
    content_en = models.TextField(blank=True, verbose_name="Content (English)")
    content_ru = models.TextField(blank=True, verbose_name="Content (Russian)")
    
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subpages', verbose_name="Parent Page")
    image = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="Sahypa suraty (TM / Esasy)")
    image_en = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="Sahypa suraty (English)")
    image_ru = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="Sahypa suraty (Russian)")
    pdf_file = models.FileField(upload_to='pages/pdf/', blank=True, null=True, verbose_name="PDF Resminama (PDF File)")
    pdf_title_tm = models.CharField(max_length=255, blank=True, verbose_name="PDF ady (Turkmen)")
    pdf_title_en = models.CharField(max_length=255, blank=True, verbose_name="PDF ady (English)")
    pdf_title_ru = models.CharField(max_length=255, blank=True, verbose_name="PDF ady (Russian)")
    source_name_tm = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (Turkmen)")
    source_name_en = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (English)")
    source_name_ru = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (Russian)")
    source_name = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (Esasy)")
    source_url = models.URLField(max_length=1000, blank=True, verbose_name="Çeşme URL (Asyl sahypanyň salgysy)")
    show_in_tm = models.BooleanField(default=True, verbose_name="Türkmen dilinde görkezilsin (TM)")
    show_in_en = models.BooleanField(default=True, verbose_name="Iňlis dilinde görkezilsin (EN)")
    show_in_ru = models.BooleanField(default=True, verbose_name="Rus dilinde görkezilsin (RU)")
    order = models.IntegerField(default=0, verbose_name="Order")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Döredilen senesi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Üýtgedilen senesi")

    def is_visible_in_lang(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if 'eng' in l or l == 'en':
            return self.show_in_en
        if 'rus' in l or l == 'ru':
            return self.show_in_ru
        return self.show_in_tm

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

    def get_source_name(self, lang='tm'):
        l = str(lang or 'tm').lower()
        name = ''
        if ('eng' in l or l == 'en') and self.source_name_en:
            name = self.source_name_en.strip()
        elif ('rus' in l or l == 'ru') and self.source_name_ru:
            name = self.source_name_ru.strip()
        elif self.source_name_tm:
            name = self.source_name_tm.strip()
        elif self.source_name:
            name = self.source_name.strip()

        if name:
            return name

        if self.source_url:
            import urllib.parse
            try:
                domain = urllib.parse.urlparse(self.source_url).netloc
                return domain.replace('www.', '')
            except Exception:
                return self.source_url
        return ''

    @property
    def display_source_name(self):
        return self.get_source_name('tm')

    def get_pdf_title(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en'):
            if self.pdf_title_en and self.pdf_title_en.strip():
                return self.pdf_title_en.strip()
            if self.title_en and self.title_en.strip():
                return self.title_en.strip()
            if self.pdf_title_tm and self.pdf_title_tm.strip():
                return self.pdf_title_tm.strip()
            return self.title_tm or str(self)
        if ('rus' in l or l == 'ru'):
            if self.pdf_title_ru and self.pdf_title_ru.strip():
                return self.pdf_title_ru.strip()
            if self.title_ru and self.title_ru.strip():
                return self.title_ru.strip()
            if self.pdf_title_tm and self.pdf_title_tm.strip():
                return self.pdf_title_tm.strip()
            return self.title_tm or str(self)
        if self.pdf_title_tm and self.pdf_title_tm.strip():
            return self.pdf_title_tm.strip()
        return self.title_tm or str(self)

    class Meta:
        ordering = ['order', 'title_tm']
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        if self.parent:
            return f"{self.parent.title_tm} -> {self.title_tm}"
        return self.title_tm

    def get_section_display_name(self):
        return dict(self.SECTION_CHOICES).get(self.section, 'Beýleki')

    def save(self, *args, **kwargs):
        if self.parent and self.parent.section and (not self.section or self.section == 'other' or self.section != self.parent.section):
            self.section = self.parent.section
        super().save(*args, **kwargs)


class SliderImage(models.Model):
    image = models.ImageField(upload_to='slides/', blank=True, null=True, verbose_name="Slider Image (TM / Esasy)")
    image_en = models.ImageField(upload_to='slides/', blank=True, null=True, verbose_name="Slider Image (English)")
    image_ru = models.ImageField(upload_to='slides/', blank=True, null=True, verbose_name="Slider Image (Russian)")
    video = models.FileField(upload_to='slides/videos/', blank=True, null=True, verbose_name="Slider Video (MP4/WebM)")
    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    subtitle_tm = models.CharField(max_length=255, blank=True, verbose_name="Subtitle (Turkmen)")
    subtitle_en = models.CharField(max_length=255, blank=True, verbose_name="Subtitle (English)")
    subtitle_ru = models.CharField(max_length=255, blank=True, verbose_name="Subtitle (Russian)")
    
    link = models.URLField(blank=True, verbose_name="Link URL")
    order = models.IntegerField(default=0, verbose_name="Order")

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

    class Meta:
        ordering = ['order']
        verbose_name = "Slider Image"
        verbose_name_plural = "Slider Images"

    def __str__(self):
        return f"{self.title_tm} (Order: {self.order})"


class News(models.Model):
    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    content_tm = models.TextField(verbose_name="Content (Turkmen)")
    content_en = models.TextField(blank=True, verbose_name="Content (English)")
    content_ru = models.TextField(blank=True, verbose_name="Content (Russian)")
    
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Surat (TM / Esasy)")
    image_en = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Surat (English)")
    image_ru = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Surat (Russian)")
    video = models.FileField(upload_to='news/videos/', blank=True, null=True, verbose_name="Wideo (Video - MP4/WebM)")
    video_url = models.URLField(blank=True, verbose_name="Wideo URL (YouTube / Çeşme)")
    source_name_tm = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (Turkmen)")
    source_name_en = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (English)")
    source_name_ru = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (Russian)")
    source_name = models.CharField(max_length=255, blank=True, verbose_name="Çeşme ady (Esasy)")
    source_url = models.URLField(max_length=1000, blank=True, verbose_name="Çeşme URL (Habaryň asyl salgysy)")
    pdf_file = models.FileField(upload_to='news/pdf/', blank=True, null=True, verbose_name="PDF Resminama (PDF File)")
    pdf_title_tm = models.CharField(max_length=255, blank=True, verbose_name="PDF ady (Turkmen)")
    pdf_title_en = models.CharField(max_length=255, blank=True, verbose_name="PDF ady (English)")
    pdf_title_ru = models.CharField(max_length=255, blank=True, verbose_name="PDF ady (Russian)")
    published_date = models.DateTimeField(default=timezone.now, verbose_name="Published Date")
    views_count = models.IntegerField(default=0, verbose_name="Views Count")

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

    def get_source_name(self, lang='tm'):
        l = str(lang or 'tm').lower()
        name = ''
        if ('eng' in l or l == 'en') and self.source_name_en:
            name = self.source_name_en.strip()
        elif ('rus' in l or l == 'ru') and self.source_name_ru:
            name = self.source_name_ru.strip()
        elif self.source_name_tm:
            name = self.source_name_tm.strip()
        elif self.source_name:
            name = self.source_name.strip()

        if name:
            return name

        if self.source_url:
            import urllib.parse
            try:
                domain = urllib.parse.urlparse(self.source_url).netloc
                return domain.replace('www.', '')
            except Exception:
                return self.source_url
        return ''

    @property
    def display_source_name(self):
        return self.get_source_name('tm')

    def get_pdf_title(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en'):
            if self.pdf_title_en and self.pdf_title_en.strip():
                return self.pdf_title_en.strip()
            if self.title_en and self.title_en.strip():
                return self.title_en.strip()
            if self.pdf_title_tm and self.pdf_title_tm.strip():
                return self.pdf_title_tm.strip()
            return self.title_tm or str(self)
        if ('rus' in l or l == 'ru'):
            if self.pdf_title_ru and self.pdf_title_ru.strip():
                return self.pdf_title_ru.strip()
            if self.title_ru and self.title_ru.strip():
                return self.title_ru.strip()
            if self.pdf_title_tm and self.pdf_title_tm.strip():
                return self.pdf_title_tm.strip()
            return self.title_tm or str(self)
        if self.pdf_title_tm and self.pdf_title_tm.strip():
            return self.pdf_title_tm.strip()
        return self.title_tm or str(self)

    class Meta:
        ordering = ['-published_date']
        verbose_name = "News"
        verbose_name_plural = "News List"

    def __str__(self):
        return self.title_tm

    @property
    def has_media(self):
        return bool(self.image or self.image_en or self.image_ru or self.video or self.video_url)

    @property
    def youtube_embed_url(self):
        if not self.video_url:
            return ''
        url = self.video_url.strip()
        import re
        yt_match = re.search(r'(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
        if yt_match:
            return f"https://www.youtube.com/embed/{yt_match.group(1)}"
        return ''


class BilimNews(models.Model):
    external_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="Bilim.tm ID")
    
    # Titles
    title_tm = models.CharField(max_length=500, default='', verbose_name="Sözbasy (TM)")
    title_en = models.CharField(max_length=500, blank=True, default='', verbose_name="Title (EN)")
    title_ru = models.CharField(max_length=500, blank=True, default='', verbose_name="Заголовок (RU)")
    
    slug = models.SlugField(max_length=400, blank=True, verbose_name="Slug")
    
    # Descriptions
    description_tm = models.TextField(blank=True, default='', verbose_name="Gysgaça beýany (TM)")
    description_en = models.TextField(blank=True, default='', verbose_name="Description (EN)")
    description_ru = models.TextField(blank=True, default='', verbose_name="Описание (RU)")
    
    # Contents
    content_tm = models.TextField(blank=True, default='', verbose_name="Mazmuny (TM)")
    content_en = models.TextField(blank=True, default='', verbose_name="Content (EN)")
    content_ru = models.TextField(blank=True, default='', verbose_name="Содержание (RU)")

    image_url = models.URLField(max_length=700, blank=True, verbose_name="Surat URL (bilim.tm)")
    image = models.ImageField(upload_to='bilim_news/', blank=True, null=True, verbose_name="Ýerli Surat (TM / Esasy)")
    image_en = models.ImageField(upload_to='bilim_news/', blank=True, null=True, verbose_name="Ýerli Surat (English)")
    image_ru = models.ImageField(upload_to='bilim_news/', blank=True, null=True, verbose_name="Ýerli Surat (Russian)")
    source_url = models.URLField(max_length=700, blank=True, verbose_name="Çeşme URL")
    pdf_file = models.FileField(upload_to='bilim_news/pdf/', blank=True, null=True, verbose_name="PDF Resminama (PDF File)")
    pdf_title_tm = models.CharField(max_length=500, blank=True, default='', verbose_name="PDF ady (Turkmen)")
    pdf_title_en = models.CharField(max_length=500, blank=True, default='', verbose_name="PDF ady (English)")
    pdf_title_ru = models.CharField(max_length=500, blank=True, default='', verbose_name="PDF ady (Russian)")
    published_date = models.DateTimeField(default=timezone.now, verbose_name="Çap edilen senesi")
    views_count = models.IntegerField(default=0, verbose_name="Görülen sany")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

    def get_pdf_title(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en'):
            if self.pdf_title_en and self.pdf_title_en.strip():
                return self.pdf_title_en.strip()
            if self.title_en and self.title_en.strip():
                return self.title_en.strip()
            if self.pdf_title_tm and self.pdf_title_tm.strip():
                return self.pdf_title_tm.strip()
            return self.title_tm or str(self)
        if ('rus' in l or l == 'ru'):
            if self.pdf_title_ru and self.pdf_title_ru.strip():
                return self.pdf_title_ru.strip()
            if self.title_ru and self.title_ru.strip():
                return self.title_ru.strip()
            if self.pdf_title_tm and self.pdf_title_tm.strip():
                return self.pdf_title_tm.strip()
            return self.title_tm or str(self)
        if self.pdf_title_tm and self.pdf_title_tm.strip():
            return self.pdf_title_tm.strip()
        return self.title_tm or str(self)

    class Meta:
        ordering = ['-published_date', '-id']
        verbose_name = "Bilim Täzeligi"
        verbose_name_plural = "Bilim Täzelikleri"

    def __str__(self):
        return self.title_tm or "Bilim News"

    @property
    def title(self):
        return self.title_tm

    @property
    def description(self):
        return self.description_tm

    @property
    def content(self):
        return self.content_tm

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''


class Faculty(models.Model):
    name_tm = models.CharField(max_length=255, verbose_name="Name (Turkmen)")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="Name (English)")
    name_ru = models.CharField(max_length=255, blank=True, verbose_name="Name (Russian)")
    
    description_tm = models.TextField(verbose_name="Description (Turkmen)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    description_ru = models.TextField(blank=True, verbose_name="Description (Russian)")
    
    dean_name_tm = models.CharField(max_length=255, blank=True, verbose_name="Dean Name (Turkmen)")
    dean_name_en = models.CharField(max_length=255, blank=True, verbose_name="Dean Name (English)")
    dean_name_ru = models.CharField(max_length=255, blank=True, verbose_name="Dean Name (Russian)")
    
    image = models.ImageField(upload_to='faculties/', blank=True, null=True, verbose_name="Surat (TM / Esasy)")
    image_en = models.ImageField(upload_to='faculties/', blank=True, null=True, verbose_name="Surat (EN)")
    image_ru = models.ImageField(upload_to='faculties/', blank=True, null=True, verbose_name="Surat (RU)")

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

    class Meta:
        verbose_name = "Faculty"
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.name_tm


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, related_name='departments', on_delete=models.CASCADE)
    
    name_tm = models.CharField(max_length=255, verbose_name="Name (Turkmen)")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="Name (English)")
    name_ru = models.CharField(max_length=255, blank=True, verbose_name="Name (Russian)")
    
    description_tm = models.TextField(verbose_name="Description (Turkmen)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    description_ru = models.TextField(blank=True, verbose_name="Description (Russian)")
    
    head_name_tm = models.CharField(max_length=255, blank=True, verbose_name="Head Name (Turkmen)")
    head_name_en = models.CharField(max_length=255, blank=True, verbose_name="Head Name (English)")
    head_name_ru = models.CharField(max_length=255, blank=True, verbose_name="Head Name (Russian)")

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.name_tm} ({self.faculty.name_tm})"


class Olympiad(models.Model):
    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    year = models.IntegerField(default=2026, verbose_name="Year")
    
    description_tm = models.TextField(blank=True, verbose_name="Description (Turkmen)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    description_ru = models.TextField(blank=True, verbose_name="Description (Russian)")
    
    results_pdf = models.FileField(upload_to='olympiads/results/', blank=True, null=True, verbose_name="Results PDF")

    class Meta:
        ordering = ['-year', 'title_tm']
        verbose_name = "Olympiad"
        verbose_name_plural = "Olympiads"

    def __str__(self):
        return f"{self.title_tm} ({self.year})"


class Partner(models.Model):
    name_tm = models.CharField(max_length=255, verbose_name="Name (Turkmen)")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="Name (English)")
    name_ru = models.CharField(max_length=255, blank=True, verbose_name="Name (Russian)")
    
    logo = models.ImageField(upload_to='partners/')
    
    country_tm = models.CharField(max_length=255, blank=True, verbose_name="Country (Turkmen)")
    country_en = models.CharField(max_length=255, blank=True, verbose_name="Country (English)")
    country_ru = models.CharField(max_length=255, blank=True, verbose_name="Country (Russian)")

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"

    def __str__(self):
        return self.name_tm


class Document(models.Model):
    CATEGORY_CHOICES = [
        ('Resminama', 'Resminamalar (Official Documents)'),
        ('Maglumat', 'Maglumatlar / Faýllar (Files & Info)'),
        ('Gollanma', 'Gollanmalar we Düzgünnamalar (Guidelines)'),
        ('Hasabat', 'Hepdelik Hasabat (Weekly Report)'),
        ('Maksatnama', 'Maksatnamalar (Programs)'),
        ('Kitaphana', 'Kitaphana (Library)'),
        ('Sanly Bilim', 'Sanly Bilim (Digital Education)'),
        ('Basga', 'Başga (Other)'),
    ]
    
    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    image = models.ImageField(upload_to='documents/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (TM / Esasy)")
    image_en = models.ImageField(upload_to='documents/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (English)")
    image_ru = models.ImageField(upload_to='documents/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (Russian)")
    file = models.FileField(upload_to='documents/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Resminama', blank=True, verbose_name="Category")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return self.title_tm


class ContactMessage(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=255, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Is Read")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class SiteSettings(models.Model):
    """Singleton model — site-wide settings editable from the custom admin panel."""

    # Institute Branding / Logo & Name
    logo = models.ImageField(upload_to='settings/logo/', blank=True, null=True, verbose_name="Baş Sahypa Logo Suraty")
    logo_title_tm = models.CharField(max_length=255, blank=True, default="TÜRKMEN DÖWLET", verbose_name="Logo Başlyk 1-nji setir (TM)")
    logo_subtitle_tm = models.CharField(max_length=255, blank=True, default="MALIÝE INSTITUTY", verbose_name="Logo Başlyk 2-nji setir (TM)")
    logo_title_en = models.CharField(max_length=255, blank=True, default="TURKMEN STATE", verbose_name="Logo Title Line 1 (EN)")
    logo_subtitle_en = models.CharField(max_length=255, blank=True, default="FINANCE INSTITUTE", verbose_name="Logo Title Line 2 (EN)")
    logo_title_ru = models.CharField(max_length=255, blank=True, default="ТУРКМЕНСКИЙ ГОСУДАРСТВЕННЫЙ", verbose_name="Logo Title Line 1 (RU)")
    logo_subtitle_ru = models.CharField(max_length=255, blank=True, default="ФИНАНСОВЫЙ ИНСТИТУТ", verbose_name="Logo Title Line 2 (RU)")

    # Statistics
    stat_books = models.CharField(max_length=100, default="45 000+", verbose_name="Books Count Text")
    stat_majors = models.CharField(max_length=100, default="12", verbose_name="Majors Count Text")
    stat_teachers = models.CharField(max_length=100, default="280+", verbose_name="Teachers Count Text")
    stat_students = models.CharField(max_length=100, default="3 200+", verbose_name="Students Count Text")
    
    stat_books_icon = models.ImageField(upload_to='settings/stats/', blank=True, null=True, verbose_name="Books Stat Icon / Logo")
    stat_majors_icon = models.ImageField(upload_to='settings/stats/', blank=True, null=True, verbose_name="Majors Stat Icon / Logo")
    stat_teachers_icon = models.ImageField(upload_to='settings/stats/', blank=True, null=True, verbose_name="Teachers Stat Icon / Logo")
    stat_students_icon = models.ImageField(upload_to='settings/stats/', blank=True, null=True, verbose_name="Students Stat Icon / Logo")

    stats_bg_image = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name="Statistika Arka Fon Suraty (Stats Background Image)")

    # Contact Info
    address_tm = models.CharField(max_length=500, blank=True, default="744027, Aşgabat ş., 1987 köç. (Hero Atamyrat Niyazow Ave.), 112.", verbose_name="Address (Turkmen)")
    address_en = models.CharField(max_length=500, blank=True, verbose_name="Address (English)")
    address_ru = models.CharField(max_length=500, blank=True, verbose_name="Address (Russian)")
    phone = models.CharField(max_length=50, blank=True, default="+993 12 496309", verbose_name="Phone")
    phone2 = models.CharField(max_length=50, blank=True, verbose_name="Phone 2 (Goşmaça)")
    email = models.EmailField(blank=True, default="info@tdmai.edu.tm", verbose_name="Email")

    # Social Media
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube URL")
    telegram_url = models.URLField(blank=True, verbose_name="Telegram URL")
    tiktok_url = models.URLField(blank=True, verbose_name="TikTok URL")

    # Footer Branding (1-nji sütün: Logo/At we Düşündiriş)
    footer_title_tm = models.CharField(max_length=255, blank=True, default="TDMai", verbose_name="Footer Başlyk (TM)")
    footer_title_en = models.CharField(max_length=255, blank=True, default="TDMai", verbose_name="Footer Title (EN)")
    footer_title_ru = models.CharField(max_length=255, blank=True, default="ТГФИ", verbose_name="Footer Title (RU)")
    footer_desc_tm = models.TextField(blank=True, default="Türkmenistanyň ykdysady we maliýe pudaklary üçin ýokary derejeli hünärmenleri taýýarlaýan öňdebaryjy ýokary okuw mekdebi.", verbose_name="Footer Düşündiriş (TM)")
    footer_desc_en = models.TextField(blank=True, default="A leading higher educational institution training top-level specialists for the economic and financial sectors of Turkmenistan.", verbose_name="Footer Description (EN)")
    footer_desc_ru = models.TextField(blank=True, default="Ведущее высшее учебное заведение, готовящее специалистов высшей квалификации для экономической и финансовой сфер Туркменистана.", verbose_name="Footer Description (RU)")

    # Footer Column 2 (2-nji sütün: Institut we Çykgytlar)
    footer_col2_title_tm = models.CharField(max_length=255, blank=True, default="Institut", verbose_name="Footer 2-nji sütün başlyk (TM)")
    footer_col2_title_en = models.CharField(max_length=255, blank=True, default="Institute", verbose_name="Footer Col 2 Title (EN)")
    footer_col2_title_ru = models.CharField(max_length=255, blank=True, default="Институт", verbose_name="Footer Col 2 Title (RU)")

    footer_col2_l1_text_tm = models.CharField(max_length=255, blank=True, default="Taryhy", verbose_name="2-nji sütün 1-nji link ýazgysy (TM)")
    footer_col2_l1_text_en = models.CharField(max_length=255, blank=True, default="History", verbose_name="Col 2 Link 1 Text (EN)")
    footer_col2_l1_text_ru = models.CharField(max_length=255, blank=True, default="История", verbose_name="Col 2 Link 1 Text (RU)")
    footer_col2_l1_url = models.CharField(max_length=255, blank=True, default="/?lang=tm#taryhy", verbose_name="2-nji sütün 1-nji link URL")

    footer_col2_l2_text_tm = models.CharField(max_length=255, blank=True, default="Olimpiadalar", verbose_name="2-nji sütün 2-nji link ýazgysy (TM)")
    footer_col2_l2_text_en = models.CharField(max_length=255, blank=True, default="Olympiads", verbose_name="Col 2 Link 2 Text (EN)")
    footer_col2_l2_text_ru = models.CharField(max_length=255, blank=True, default="Олимпиады", verbose_name="Col 2 Link 2 Text (RU)")
    footer_col2_l2_url = models.CharField(max_length=255, blank=True, default="/olympiads/", verbose_name="2-nji sütün 2-nji link URL")

    footer_col2_l3_text_tm = models.CharField(max_length=255, blank=True, default="Täzelikler", verbose_name="2-nji sütün 3-nji link ýazgysy (TM)")
    footer_col2_l3_text_en = models.CharField(max_length=255, blank=True, default="News", verbose_name="Col 2 Link 3 Text (EN)")
    footer_col2_l3_text_ru = models.CharField(max_length=255, blank=True, default="Новости", verbose_name="Col 2 Link 3 Text (RU)")
    footer_col2_l3_url = models.CharField(max_length=255, blank=True, default="/news/", verbose_name="2-nji sütün 3-nji link URL")

    footer_col2_l4_text_tm = models.CharField(max_length=255, blank=True, default="Kitaphana", verbose_name="2-nji sütün 4-nji link ýazgysy (TM)")
    footer_col2_l4_text_en = models.CharField(max_length=255, blank=True, default="Library", verbose_name="Col 2 Link 4 Text (EN)")
    footer_col2_l4_text_ru = models.CharField(max_length=255, blank=True, default="Библиотека", verbose_name="Col 2 Link 4 Text (RU)")
    footer_col2_l4_url = models.CharField(max_length=255, blank=True, default="/library/1/", verbose_name="2-nji sütün 4-nji link URL")

    # Footer Column 3 (3-nji sütün: Fakultetler)
    footer_col3_title_tm = models.CharField(max_length=255, blank=True, default="Fakultetler", verbose_name="Footer 3-nji sütün başlyk (TM)")
    footer_col3_title_en = models.CharField(max_length=255, blank=True, default="Faculties", verbose_name="Footer Col 3 Title (EN)")
    footer_col3_title_ru = models.CharField(max_length=255, blank=True, default="Факультеты", verbose_name="Footer Col 3 Title (RU)")

    # Footer Column 4 (4-nji sütün: Habarlaşmak)
    footer_col4_title_tm = models.CharField(max_length=255, blank=True, default="Habarlaşmak", verbose_name="Footer 4-nji sütün başlyk (TM)")
    footer_col4_title_en = models.CharField(max_length=255, blank=True, default="Contact", verbose_name="Footer Col 4 Title (EN)")
    footer_col4_title_ru = models.CharField(max_length=255, blank=True, default="Контакты", verbose_name="Footer Col 4 Title (RU)")

    # Footer Bottom Copyright
    copyright_text_tm = models.CharField(max_length=500, blank=True, default="© Hemme hukuklary goralan - 2026. Türkmen Döwlet Maliýe Instituty.", verbose_name="Copyright (TM)")
    copyright_text_en = models.CharField(max_length=500, blank=True, default="© All rights reserved - 2026. Turkmen State Finance Institute.", verbose_name="Copyright (EN)")
    copyright_text_ru = models.CharField(max_length=500, blank=True, default="© Все права защищены - 2026. Туркменский государственный финансовый институт.", verbose_name="Copyright (RU)")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_settings(cls):
        """Always return the single settings object, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class LibraryCategory(models.Model):
    name_tm = models.CharField(max_length=255, verbose_name="Kategoriýa Ady (Turkmen)")
    name_en = models.CharField(max_length=255, blank=True, verbose_name="Category Name (English)")
    name_ru = models.CharField(max_length=255, blank=True, verbose_name="Category Name (Russian)")
    
    icon = models.ImageField(upload_to='library_icons/', blank=True, null=True, verbose_name="Icon / Logo")
    order = models.IntegerField(default=0, verbose_name="Tertip belgisi (Order)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Döredilen senesi")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Neşir Kategoriýasy"
        verbose_name_plural = "Neşir Kategoriýalary"

    def __str__(self):
        return self.name_tm


class LibraryBook(models.Model):
    category = models.ForeignKey(
        LibraryCategory,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name="Kategoriýasy (Neşir)"
    )
    title_tm = models.CharField(max_length=255, verbose_name="Sözbaşy / Ady (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    pdf_file = models.FileField(upload_to='library_books/', blank=True, null=True, verbose_name="PDF Faýl")
    image = models.ImageField(upload_to='library_books/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (TM / Esasy)")
    image_en = models.ImageField(upload_to='library_books/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (English)")
    image_ru = models.ImageField(upload_to='library_books/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (Russian)")
    cover_image = models.ImageField(upload_to='library_books/covers/', blank=True, null=True, verbose_name="Daşky suraty (Cover)")
    year = models.IntegerField(default=2026, blank=True, null=True, verbose_name="Ýyly")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ýüklenen senesi")

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image or self.cover_image

    @property
    def display_image(self):
        return self.image or self.cover_image

    class Meta:

        ordering = ['-year', '-uploaded_at', '-id']
        verbose_name = "Neşir Sany / Kitap"
        verbose_name_plural = "Neşir Sanlary / Kitaplar"

    def __str__(self):
        return f"{self.title_tm} ({self.category.name_tm})"

