from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('faculty/<int:pk>/', views.faculty_detail, name='faculty_detail'),
    path('department/<int:pk>/', views.department_detail, name='department_detail'),
    path('olympiads/', views.olympiads, name='olympiads'),
    path('contact/', views.contact, name='contact'),
    path('set-language/', views.set_language, name='set_language'),
    path('p/<slug:slug>/', views.page_detail, name='page_detail'),
]
