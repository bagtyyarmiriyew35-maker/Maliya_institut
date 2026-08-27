from django.db import models
from django.utils import timezone

class Page(models.Model):
    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    
    content_tm = models.TextField(blank=True, verbose_name="Content (Turkmen)")
    content_en = models.TextField(blank=True, verbose_name="Content (English)")
    content_ru = models.TextField(blank=True, verbose_name="Content (Russian)")
    
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subpages', verbose_name="Parent Page")
    order = models.IntegerField(default=0, verbose_name="Order")

    class Meta:
        ordering = ['order', 'title_tm']
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        if self.parent:
            return f"{self.parent.title_tm} -> {self.title_tm}"
        return self.title_tm


class SliderImage(models.Model):
    image = models.ImageField(upload_to='slides/')
    title_tm = models.CharField(max_length=255, verbose_name="Title (Turkmen)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=255, blank=True, verbose_name="Title (Russian)")
    
    subtitle_tm = models.CharField(max_length=255, blank=True, verbose_name="Subtitle (Turkmen)")
    subtitle_en = models.CharField(max_length=255, blank=True, verbose_name="Subtitle (English)")
    subtitle_ru = models.CharField(max_length=255, blank=True, verbose_name="Subtitle (Russian)")
    
    link = models.URLField(blank=True, verbose_name="Link URL")
    order = models.IntegerField(default=0, verbose_name="Order")

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
    
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_date = models.DateTimeField(default=timezone.now, verbose_name="Published Date")
    views_count = models.IntegerField(default=0, verbose_name="Views Count")

    class Meta:
        ordering = ['-published_date']
        verbose_name = "News"
        verbose_name_plural = "News List"

    def __str__(self):
        return self.title_tm


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
    
    image = models.ImageField(upload_to='faculties/', blank=True, null=True)

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
    
    file = models.FileField(upload_to='documents/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Hasabat', verbose_name="Category")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")

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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
