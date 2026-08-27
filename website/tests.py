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
