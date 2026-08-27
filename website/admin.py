from django.contrib import admin
from .models import Page, SliderImage, News, Faculty, Department, Olympiad, Partner, Document, ContactMessage

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title_tm', 'slug', 'parent', 'order')
    list_filter = ('parent',)
    search_fields = ('title_tm', 'title_en', 'title_ru', 'content_tm', 'slug')
    prepopulated_fields = {'slug': ('title_tm',)}


@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('title_tm', 'order', 'link')
    list_editable = ('order',)
    search_fields = ('title_tm', 'title_en', 'title_ru', 'subtitle_tm')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title_tm', 'published_date', 'views_count')
    list_filter = ('published_date',)
    search_fields = ('title_tm', 'title_en', 'title_ru', 'content_tm', 'content_en', 'content_ru')
    readonly_fields = ('views_count',)


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name_tm', 'dean_name_tm')
    search_fields = ('name_tm', 'name_en', 'name_ru', 'dean_name_tm')
    inlines = [DepartmentInline]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_tm', 'faculty', 'head_name_tm')
    list_filter = ('faculty',)
    search_fields = ('name_tm', 'name_en', 'name_ru', 'head_name_tm')


@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    list_display = ('title_tm', 'year')
    list_filter = ('year',)
    search_fields = ('title_tm', 'title_en', 'title_ru')


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name_tm', 'country_tm')
    search_fields = ('name_tm', 'name_en', 'name_ru', 'country_tm')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title_tm', 'category', 'uploaded_at')
    list_filter = ('category', 'uploaded_at')
    search_fields = ('title_tm', 'title_en', 'title_ru')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    
    def has_add_permission(self, request):
        return False  # messages come from the public site form only
