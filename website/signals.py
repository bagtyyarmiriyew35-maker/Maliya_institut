from django.db.models.signals import pre_save
from django.dispatch import receiver
from .media_optimizer import convert_image_to_webp, convert_video_to_webm
from .models import (
    Page, SliderImage, News, BilimNews, Faculty,
    Partner, Document, SiteSettings, LibraryCategory, LibraryBook
)

IMAGE_FIELD_MAPPING = {
    Page: ['image', 'image_en', 'image_ru'],
    SliderImage: ['image', 'image_en', 'image_ru'],
    News: ['image', 'image_en', 'image_ru'],
    BilimNews: ['image', 'image_en', 'image_ru'],
    Faculty: ['image', 'image_en', 'image_ru'],
    Partner: ['logo'],
    Document: ['image', 'image_en', 'image_ru'],
    SiteSettings: ['logo', 'stat_books_icon', 'stat_majors_icon', 'stat_teachers_icon', 'stat_students_icon', 'stats_bg_image'],
    LibraryCategory: ['icon'],
    LibraryBook: ['image', 'image_en', 'image_ru', 'cover_image'],
}

VIDEO_FIELD_MAPPING = {
    SliderImage: ['video'],
    News: ['video'],
}


@receiver(pre_save)
def auto_optimize_uploaded_media(sender, instance, **kwargs):
    """
    Automatically converts any newly uploaded image to WebP,
    and any newly uploaded video to WebM before saving to database.
    """
    # Skip during fixture loading (e.g. loaddata)
    if kwargs.get('raw', False):
        return
    # 1. Process Images -> WebP
    if sender in IMAGE_FIELD_MAPPING:
        for field_name in IMAGE_FIELD_MAPPING[sender]:
            field_file = getattr(instance, field_name, None)
            if field_file:
                # Max width for icons vs standard pictures
                max_w = 512 if 'icon' in field_name or field_name == 'logo' else 1920
                new_webp = convert_image_to_webp(field_file, max_width=max_w, quality=82)
                if new_webp:
                    setattr(instance, field_name, new_webp)

    # 2. Process Videos -> WebM
    if sender in VIDEO_FIELD_MAPPING:
        for field_name in VIDEO_FIELD_MAPPING[sender]:
            field_file = getattr(instance, field_name, None)
            if field_file:
                new_webm = convert_video_to_webm(field_file)
                if new_webm:
                    setattr(instance, field_name, new_webm)
