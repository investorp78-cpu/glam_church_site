from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sermons/', views.sermons, name='sermons'),
    path('events/', views.events, name='events'),
    path('about/', views.about, name='about'),
    path('give/', views.give, name='give'),
    path('contact/', views.contact, name='contact'),
    path('new-visitor/', views.new_visitor, name='new_visitor'),
    path('testimonies/', views.testimonies_page, name='testimonies'),
    path('testimonies/submit/', views.testimony_submit_page, name='testimony_submit'),
    path('testimony/<int:pk>/', views.testimony_detail, name='testimony_detail'),
    path('live/', views.live_page, name='live'),
    path('submit-testimony/', views.submit_testimony, name='submit_testimony'),
    path('save-push-subscription/', views.save_push_subscription, name='save_push'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/update-profile/', views.update_profile, name='update_profile'),
]
