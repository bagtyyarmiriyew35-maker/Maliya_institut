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
    order = models.IntegerField(default=0, verbose_name="Order")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Döredilen senesi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Üýtgedilen senesi")

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

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
    published_date = models.DateTimeField(default=timezone.now, verbose_name="Published Date")
    views_count = models.IntegerField(default=0, verbose_name="Views Count")

    def get_image(self, lang='tm'):
        l = str(lang or 'tm').lower()
        if ('eng' in l or l == 'en') and self.image_en:
            return self.image_en
        if ('rus' in l or l == 'ru') and self.image_ru:
            return self.image_ru
        return self.image

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
        ('Kitaphana', 'Kitaphana (Library)'),
        ('Sanly Bilim', 'Sanly Bilim (Digital Education)'),
        ('Hasabat', 'Hepdelik Hasabat (Weekly Report)'),
        ('Maksatnama', 'Maksatnamalar (Programs)'),
    ]
    
    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    image = models.ImageField(upload_to='documents/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (TM / Esasy)")
    image_en = models.ImageField(upload_to='documents/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (English)")
    image_ru = models.ImageField(upload_to='documents/headers/', blank=True, null=True, verbose_name="Başlyk Suraty (Russian)")
    file = models.FileField(upload_to='documents/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Hasabat', verbose_name="Category")
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
        return f"{self.title_tm} ({self.get_category_display()})"


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
    email = models.EmailField(blank=True, default="info@tdmai.edu.tm", verbose_name="Email")

    # Social Media
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube URL")

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

