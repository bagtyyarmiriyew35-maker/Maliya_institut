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
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/detail.html')

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



