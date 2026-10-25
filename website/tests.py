from django.test import TestCase
from django.urls import reverse
from website.models import Page, Faculty, Department, News, ContactMessage

class WebsiteViewsTestCase(TestCase):
    def setUp(self):
        # Create a mock Faculty & Department for testing detail views
        self.faculty = Faculty.objects.create(
            name_tm="Maliýe",
            name_en="Finance",
            description_tm="Maliýe hünärmenlerini taýýarlaýar."
        )
        self.department = Department.objects.create(
            faculty=self.faculty,
            name_tm="Maliýe we salgytlar",
            description_tm="Kafedra barada."
        )
        self.news = News.objects.create(
            title_tm="Täze bäsleşik",
            content_tm="Bäsleşigiň şertleri..."
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_news_list_page_status_code(self):
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/list.html')

    def test_news_list_pagination(self):
        for i in range(10):
            News.objects.create(title_tm=f"Täzelik {i}", content_tm="Mazmuny")
        
        response_page1 = self.client.get(reverse('news_list') + '?page=1')
        self.assertEqual(len(response_page1.context['all_news']), 6)
        
        response_page2 = self.client.get(reverse('news_list') + '?page=2')
        # 1 created in setUp + 10 created in loop = 11 total news.
        # Page 1 has 6, Page 2 has 5.
        self.assertEqual(len(response_page2.context['all_news']), 5)

    def test_news_detail_page_status_code(self):
        response = self.client.get(reverse('news_detail', args=[self.news.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/detail.html')
        
        # Test view count increment
        self.news.refresh_from_db()
        self.assertEqual(self.news.views_count, 1)

    def test_faculty_detail_page_status_code(self):
        response = self.client.get(reverse('faculty_detail', args=[self.faculty.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/faculty_detail.html')

    def test_department_detail_page_status_code(self):
        response = self.client.get(reverse('department_detail', args=[self.department.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/department_detail.html')

    def test_olympiads_page_status_code(self):
        response = self.client.get(reverse('olympiads'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'olympiads/list.html')

    def test_contact_page_status_code(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_contact_form_submission(self):
        data = {
            'name': 'Gurban',
            'email': 'gurban@gmail.com',
            'subject': 'Soraşmak',
            'message': 'Sapaklar haçan başlaýar?'
        }
        response = self.client.post(reverse('contact'), data)
        self.assertEqual(response.status_code, 302) # Should redirect after submission
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Gurban')
        self.assertEqual(msg.subject, 'Soraşmak')

    def test_language_switcher(self):
        response = self.client.get(reverse('set_language') + '?lang=eng')
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertEqual(self.client.session['lang'], 'eng')

    def test_dynamic_page_detail_page_status_code(self):
        page = Page.objects.create(
            title_tm="Taryhy",
            slug="taryhy-test",
            content_tm="Taryhy maglumat."
        )
        response = self.client.get(reverse('page_detail', args=[page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'page_detail.html')

    def test_library_detail_page_status_code(self):
        from website.models import LibraryCategory, LibraryBook
        cat = LibraryCategory.objects.create(name_tm="Bilim žurnaly")
        LibraryBook.objects.create(category=cat, title_tm="Bilim žurnaly 1 sany 2026")
        response = self.client.get(reverse('library_detail', args=[cat.pk]))
        self.assertEqual(response.status_code, 302)
        response_followed = self.client.get(reverse('library_detail', args=[cat.pk]), follow=True)
        self.assertEqual(response_followed.status_code, 200)
        self.assertTemplateUsed(response_followed, 'library/detail.html')

    def test_library_book_detail_page_status_code(self):
        from website.models import LibraryCategory, LibraryBook
        cat = LibraryCategory.objects.create(name_tm="Bilim žurnaly")
        book = LibraryBook.objects.create(category=cat, title_tm="Bilim žurnaly 2 sany 2026")
        response = self.client.get(reverse('library_book_detail', args=[book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/book_detail.html')


class MultilingualContentTestCase(TestCase):
    def setUp(self):
        self.news = News.objects.create(
            title_tm="Türkmençe Sözbasy",
            title_en="English Title",
            title_ru="Русский Заголовок",
            content_tm="Türkmençe doly mazmun.",
            content_en="English full content.",
            content_ru="Русское полное содержание."
        )
        self.faculty = Faculty.objects.create(
            name_tm="Maliýe Fakulteti",
            name_en="Finance Faculty",
            name_ru="Финансовый Факультет",
            description_tm="Türkmençe beýany.",
            description_en="English description.",
            description_ru="Русское описание.",
            dean_name_tm="Amanow A.",
            dean_name_en="Amanov A.",
            dean_name_ru="Аманов А."
        )

    def test_render_lang_tag(self):
        from website.templatetags.website_tags import render_lang, ui_label

        # Test TM
        self.assertEqual(render_lang(self.news, 'title', 'tm'), "Türkmençe Sözbasy")
        self.assertEqual(render_lang(self.news, 'content', 'tm'), "Türkmençe doly mazmun.")

        # Test EN (both 'eng' and 'en')
        self.assertEqual(render_lang(self.news, 'title', 'eng'), "English Title")
        self.assertEqual(render_lang(self.news, 'title', 'en'), "English Title")
        self.assertEqual(render_lang(self.news, 'content', 'eng'), "English full content.")

        # Test RU (both 'rus' and 'ru')
        self.assertEqual(render_lang(self.news, 'title', 'rus'), "Русский Заголовок")
        self.assertEqual(render_lang(self.news, 'title', 'ru'), "Русский Заголовок")
        self.assertEqual(render_lang(self.news, 'content', 'rus'), "Русское полное содержание.")

        # Test UI labels
        self.assertEqual(ui_label('news', 'tm'), "Täzelikler")
        self.assertEqual(ui_label('news', 'eng'), "News")
        self.assertEqual(ui_label('news', 'rus'), "Новости")
        self.assertEqual(ui_label('home', 'en'), "Home")
        self.assertEqual(ui_label('home', 'ru'), "Главная")

    def test_render_lang_fallback_to_turkmen(self):
        from website.templatetags.website_tags import render_lang

        # An item with only TM filled
        item = News.objects.create(
            title_tm="Diňe Türkmençe",
            title_en="",
            title_ru="",
            content_tm="Mazmuny diňe türkmençe.",
            content_en="",
            content_ru=""
        )

        # In English and Russian, it must fall back to Turkmen rather than being blank
        self.assertEqual(render_lang(item, 'title', 'eng'), "Diňe Türkmençe")
        self.assertEqual(render_lang(item, 'title', 'rus'), "Diňe Türkmençe")
        self.assertEqual(render_lang(item, 'content', 'eng'), "Mazmuny diňe türkmençe.")
        self.assertEqual(render_lang(item, 'content', 'rus'), "Mazmuny diňe türkmençe.")

    def test_frontend_switches_content_based_on_language(self):
        # 1. Default (TM)
        res_tm = self.client.get(reverse('news_detail', args=[self.news.pk]))
        self.assertContains(res_tm, "Türkmençe Sözbasy")

        # 2. Switch to English
        self.client.get(reverse('set_language') + '?lang=eng')
        res_en = self.client.get(reverse('news_detail', args=[self.news.pk]))
        self.assertContains(res_en, "English Title")
        self.assertContains(res_en, "English full content.")

        # 3. Switch to Russian
        self.client.get(reverse('set_language') + '?lang=rus')
        res_ru = self.client.get(reverse('news_detail', args=[self.news.pk]))
        self.assertContains(res_ru, "Русский Заголовок")
        self.assertContains(res_ru, "Русское полное содержание.")

        # 4. Switch to English using ?lang=en (short code)
        self.client.get(reverse('set_language') + '?lang=en')
        self.assertEqual(self.client.session['lang'], 'eng')

        # 5. Switch to Russian using ?lang=ru (short code)
        self.client.get(reverse('set_language') + '?lang=ru')
        self.assertEqual(self.client.session['lang'], 'rus')

    def test_multilingual_page_images(self):
        page = Page.objects.create(
            title_tm="Institut Taryhy",
            slug="institut-taryhy",
            section="institut",
            image="pages/tm_img.jpg",
            image_en="pages/en_img.jpg",
            image_ru="pages/ru_img.jpg",
        )
        self.assertEqual(page.get_image('tm').name, "pages/tm_img.jpg")
        self.assertEqual(page.get_image('eng').name, "pages/en_img.jpg")
        self.assertEqual(page.get_image('rus').name, "pages/ru_img.jpg")

        # Test fallback if EN or RU not uploaded
        page_tm_only = Page.objects.create(
            title_tm="Fallback Test",
            slug="fallback-test",
            section="institut",
            image="pages/default_img.jpg",
        )
        self.assertEqual(page_tm_only.get_image('eng').name, "pages/default_img.jpg")
        self.assertEqual(page_tm_only.get_image('rus').name, "pages/default_img.jpg")

    def test_all_models_multilingual_images(self):
        from website.models import SliderImage, BilimNews, Document, LibraryCategory, LibraryBook
        from website.templatetags.website_tags import render_multilingual_image

        # 1. SliderImage
        slide = SliderImage.objects.create(
            title_tm="Slide TM",
            image="slides/tm.jpg",
            image_en="slides/en.jpg",
            image_ru="slides/ru.jpg",
        )
        self.assertEqual(slide.get_image('tm').name, "slides/tm.jpg")
        self.assertEqual(slide.get_image('eng').name, "slides/en.jpg")
        self.assertEqual(slide.get_image('rus').name, "slides/ru.jpg")
        self.assertEqual(render_multilingual_image(slide, 'eng').name, "slides/en.jpg")

        # 2. News
        news = News.objects.create(
            title_tm="News TM",
            content_tm="Content TM",
            image="news/tm.jpg",
            image_en="news/en.jpg",
        )
        self.assertEqual(news.get_image('tm').name, "news/tm.jpg")
        self.assertEqual(news.get_image('eng').name, "news/en.jpg")
        # RU fallback to TM
        self.assertEqual(news.get_image('rus').name, "news/tm.jpg")

        # 3. BilimNews
        bilim = BilimNews.objects.create(
            title_tm="Bilim TM",
            image="bilim/tm.jpg",
            image_ru="bilim/ru.jpg",
        )
        self.assertEqual(bilim.get_image('tm').name, "bilim/tm.jpg")
        self.assertEqual(bilim.get_image('rus').name, "bilim/ru.jpg")
        # EN fallback to TM
        self.assertEqual(bilim.get_image('eng').name, "bilim/tm.jpg")

        # 4. Document
        doc = Document.objects.create(
            title_tm="Doc TM",
            category="Hasabat",
            image="docs/tm.jpg",
            image_en="docs/en.jpg",
            image_ru="docs/ru.jpg",
        )
        self.assertEqual(doc.get_image('tm').name, "docs/tm.jpg")
        self.assertEqual(doc.get_image('eng').name, "docs/en.jpg")
        self.assertEqual(doc.get_image('rus').name, "docs/ru.jpg")

        # 5. LibraryBook
        cat = LibraryCategory.objects.create(name_tm="Žurnallar")
        book = LibraryBook.objects.create(
            category=cat,
            title_tm="Book TM",
            image="books/tm.jpg",
            image_en="books/en.jpg",
            image_ru="books/ru.jpg",
        )
        self.assertEqual(book.get_image('tm').name, "books/tm.jpg")
        self.assertEqual(book.get_image('eng').name, "books/en.jpg")
        self.assertEqual(book.get_image('rus').name, "books/ru.jpg")
        self.assertEqual(book.display_image.name, "books/tm.jpg")

        # 6. Dictionary object (e.g. recent_contents)
        d_item = {
            'image_tm': 'recent/tm.jpg',
            'image_en': 'recent/en.jpg',
            'image_ru': 'recent/ru.jpg',
        }
        self.assertEqual(render_multilingual_image(d_item, 'tm'), 'recent/tm.jpg')
        self.assertEqual(render_multilingual_image(d_item, 'eng'), 'recent/en.jpg')
        self.assertEqual(render_multilingual_image(d_item, 'rus'), 'recent/ru.jpg')


class InvalidUrlTestCase(TestCase):
    def test_invalid_path_renders_custom_404_page(self):
        """Typing an unknown URL like /dsd must render custom 404 template matching design."""
        response = self.client.get('/dsd')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        content = response.content.decode('utf-8')
        self.assertIn('404', content)
        self.assertIn('Gözleýän sahypaňyz tapylmady', content)
        self.assertIn('Baş sahypa dolan', content)

    def test_invalid_path_with_lang_preserves_language(self):
        """Typing an unknown URL with lang=ru must render Russian 404 page."""
        response = self.client.get('/random-page/?lang=ru')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        content = response.content.decode('utf-8')
        self.assertIn('Запрашиваемая страница не найдена', content)
        self.assertIn('Вернуться на главную', content)

    def test_missing_static_or_media_asset_returns_404_no_template(self):
        """Missing static asset or media file must return 404 plain text."""
        response = self.client.get('/static/css/nonexistent_file_xyz.css')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')






