from django.urls import path
from . import views

urlpatterns = [
    # Add pages
    
    path('yuaidash-login/', views.login_view, name='login'),
    path('yuaidash/', views.yuaidash, name='yuaidash'),

    
    path('add-blog/', views.add_blog, name='add_blog'),
    path('admin/blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blog/edit/<int:pk>/', views.edit_blog, name='edit_blog'),
    path('blog/delete/<int:pk>/', views.delete_blog, name='delete_blog'),
    
    path('add-faq/', views.add_faq, name='add_faq'),
    
    
    path('add-services/', views.add_services, name='add_services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('services/<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('services/delete/<int:pk>', views.delete_service, name='delete_service'),
    path('services/detail/<int:pk>/delete/', views.delete_service_detail, name='delete_service_detail'),
    
    path('services/<int:service_id>/details/add/', views.add_service_details, name='add_service_details'),
    path('services/<int:service_id>/details/edit/', views.edit_service_details, name='edit_service_details'),



    path('add-team/', views.add_team, name='add_team'),
    path('team/<int:pk>/edit/', views.edit_team, name='edit_team'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:pk>/delete/', views.delete_team, name='delete_team'),
    path('team/education/<int:pk>/delete/', views.delete_education, name='delete_education'),
    path('team/experience/<int:pk>/delete/', views.delete_experience, name='delete_experience'),
    path('team/social/<int:pk>/delete/', views.delete_sociallink, name='delete_sociallink'),


    path('add-testimonial/', views.add_testimonial, name='add_testimonial'),
    path('testimonials/edit/<int:testimonial_id>/', views.edit_testimonial, name='edit_testimonial'),
    path('testimonials/delete/<int:testimonial_id>/', views.delete_testimonial, name='delete_testimonial'),
    
    # Main pages
    path('blog/', views.blog, name='blog'),
    
    path('faq-request/', views.faq_request, name='faq_request'),
    path('send-faq-response/', views.send_faq_response, name='send_faq_response'),
    path('add-to-faq/<int:userfaq_id>/', views.add_to_faq, name='add_to_faq'),
    path('faq-request/export-csv/', views.export_faq_csv, name='export_faq_csvs'),
    
        
    path('faq/', views.faq, name='faq'),
    
    path('queries/', views.queries, name='queries'),
    path('queries/export-csv/', views.export_queries_csv, name='export_queries_csv'),
    
    path('send-query-response/', views.send_query_response, name='send_query_response'),
    path('mark-query-resolved/<int:query_id>/', views.mark_query_resolved, name='mark_query_resolved'),
    
    path('ref/', views.ref, name='ref'),
    path('services/', views.services, name='services'),
    path('team/', views.team, name='team'),
    path('testimonial/', views.testimonial, name='testimonial'),
    
    path('newsletter/', views.newsletter, name='newsletter'),
    path('newsletter/add-subscriber/', views.add_subscriber, name='add_subscriber'),
    path('newsletter/toggle-subscriber/<int:subscriber_id>/', views.toggle_subscriber, name='toggle_subscriber'),
    path('newsletter/delete-subscriber/<int:subscriber_id>/', views.delete_subscriber, name='delete_subscriber'),
    path('newsletter/export-subscribers/', views.export_subscribers, name='export_subscribers'),
    path('newsletter/create-campaign/', views.create_campaign, name='create_campaign'),
    path('newsletter/send-campaign/<int:campaign_id>/', views.send_campaign, name='send_campaign'),
    path('newsletter/delete-campaign/<int:campaign_id>/', views.delete_campaign, name='delete_campaign'),
]
