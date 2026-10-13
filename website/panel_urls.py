from django.urls import path
from . import panel_views

urlpatterns = [
    # Auth
    path('login/', panel_views.panel_login, name='panel_login'),
    path('logout/', panel_views.panel_logout, name='panel_logout'),

    # Dashboard
    path('', panel_views.panel_dashboard, name='panel_dashboard'),

    # Sliders
    path('sliders/', panel_views.panel_sliders, name='panel_sliders'),
    path('sliders/add/', panel_views.panel_slider_add, name='panel_slider_add'),
    path('sliders/<int:pk>/edit/', panel_views.panel_slider_edit, name='panel_slider_edit'),
    path('sliders/<int:pk>/delete/', panel_views.panel_slider_delete, name='panel_slider_delete'),

    # News
    path('news/', panel_views.panel_news, name='panel_news'),
    path('news/add/', panel_views.panel_news_add, name='panel_news_add'),
    path('news/<int:pk>/edit/', panel_views.panel_news_edit, name='panel_news_edit'),
    path('news/<int:pk>/delete/', panel_views.panel_news_delete, name='panel_news_delete'),

    # Bilim.tm News
    path('bilim-news/', panel_views.panel_bilim_news, name='panel_bilim_news'),
    path('bilim-news/sync/', panel_views.panel_bilim_news_sync, name='panel_bilim_news_sync'),
    path('bilim-news/<int:pk>/edit/', panel_views.panel_bilim_news_edit, name='panel_bilim_news_edit'),
    path('bilim-news/<int:pk>/delete/', panel_views.panel_bilim_news_delete, name='panel_bilim_news_delete'),

    # Pages
    path('pages/', panel_views.panel_pages, name='panel_pages'),
    path('pages/section/<str:section>/', panel_views.panel_pages_by_section, name='panel_pages_by_section'),
    path('pages/<int:pk>/edit/', panel_views.panel_page_edit, name='panel_page_edit'),
    path('pages/add/', panel_views.panel_page_add, name='panel_page_add'),
    path('pages/<int:pk>/delete/', panel_views.panel_page_delete, name='panel_page_delete'),

    # Faculties
    path('faculties/', panel_views.panel_faculties, name='panel_faculties'),
    path('faculties/add/', panel_views.panel_faculty_add, name='panel_faculty_add'),
    path('faculties/<int:pk>/edit/', panel_views.panel_faculty_edit, name='panel_faculty_edit'),
    path('faculties/<int:pk>/delete/', panel_views.panel_faculty_delete, name='panel_faculty_delete'),

    # Departments
    path('departments/', panel_views.panel_departments, name='panel_departments'),
    path('departments/add/', panel_views.panel_department_add, name='panel_department_add'),
    path('departments/<int:pk>/edit/', panel_views.panel_department_edit, name='panel_department_edit'),
    path('departments/<int:pk>/delete/', panel_views.panel_department_delete, name='panel_department_delete'),

    # Documents
    path('documents/', panel_views.panel_documents, name='panel_documents'),
    path('documents/add/', panel_views.panel_document_add, name='panel_document_add'),
    path('documents/<int:pk>/edit/', panel_views.panel_document_edit, name='panel_document_edit'),
    path('documents/<int:pk>/delete/', panel_views.panel_document_delete, name='panel_document_delete'),

    # Olympiads
    path('olympiads/', panel_views.panel_olympiads, name='panel_olympiads'),
    path('olympiads/add/', panel_views.panel_olympiad_add, name='panel_olympiad_add'),
    path('olympiads/<int:pk>/edit/', panel_views.panel_olympiad_edit, name='panel_olympiad_edit'),
    path('olympiads/<int:pk>/delete/', panel_views.panel_olympiad_delete, name='panel_olympiad_delete'),

    # Partners
    path('partners/', panel_views.panel_partners, name='panel_partners'),
    path('partners/add/', panel_views.panel_partner_add, name='panel_partner_add'),
    path('partners/<int:pk>/edit/', panel_views.panel_partner_edit, name='panel_partner_edit'),
    path('partners/<int:pk>/delete/', panel_views.panel_partner_delete, name='panel_partner_delete'),

    # Messages
    path('messages/', panel_views.panel_messages, name='panel_messages'),
    path('messages/<int:pk>/delete/', panel_views.panel_message_delete, name='panel_message_delete'),
    path('messages/<int:pk>/read/', panel_views.panel_message_read, name='panel_message_read'),

    # Settings
    path('settings/', panel_views.panel_settings, name='panel_settings'),

    # Library / Journals (Elektron Žurnallar)
    path('library/categories/', panel_views.panel_library_categories, name='panel_library_categories'),
    path('library/categories/add/', panel_views.panel_library_category_add, name='panel_library_category_add'),
    path('library/categories/<int:pk>/edit/', panel_views.panel_library_category_edit, name='panel_library_category_edit'),
    path('library/categories/<int:pk>/delete/', panel_views.panel_library_category_delete, name='panel_library_category_delete'),

    path('library/books/', panel_views.panel_library_books, name='panel_library_books'),
    path('library/books/add/', panel_views.panel_library_book_add, name='panel_library_book_add'),
    path('library/books/<int:pk>/edit/', panel_views.panel_library_book_edit, name='panel_library_book_edit'),
    path('library/books/<int:pk>/delete/', panel_views.panel_library_book_delete, name='panel_library_book_delete'),
]

