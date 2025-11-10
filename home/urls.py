from django.contrib import admin
from django.urls import path
from .import views


urlpatterns = [
    path('',views.loadindex,name='loadindex'),

    path("subscribe/", views.subscribe_newsletter, name="subscribe"),
    path('contact-us/', views.contact_us_view, name='contact_us'),

    path('about-us/',views.loadaboutus,name='loadaboutus'),
    path('our-team/',views.loadteam,name='loadteam'),
    path('team-details/<int:id>',views.loadteamdetails,name='loadteamdetails'),
    path('testimonial/',views.loadtestimonial,name='loadtestimonial'),
    path('faq/',views.loadfaq,name='loadfaq'),
    path('contact/',views.loadcontact,name='loadcontact'),
    path('service/',views.loadservice,name='loadservice'),
    path('services/<int:service_id>/', views.loadservicedetails, name='loadservicedetails'),
    path('blog-grid',views.loadbloggrid,name='loadbloggrid'),

    path('blog-column',views.loadblog,name='loadblog'),
    path('search',views.Searching,name='search'),
    path('<slug:Bslug>',views.loadblogdetails,name='loadblogdetails'),
  
]
