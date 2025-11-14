from django.contrib import admin
# Register your models here.
from .models import Team
from .models import Experience
from .models import Education
from .models import SocialLink
from .models import Testimonial
from .models import ContactUs
from .models import AdminFAQ
from .models import UserFAQ
from .models import Blog
from .models import BlogImage
from .models import BlogComment
from .models import Service
from .models import ServiceDetail
from .models import NewsletterSubscriber



class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'email', 'phone_number', 'skills', 'experience_years', 'current_project', 'portfolio', 'cv', 'status']
    list_editable = ['role', 'email', 'phone_number', 'skills', 'experience_years', 'current_project', 'portfolio', 'cv', 'status']
admin.site.register(Team, TeamAdmin)

class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'company_name', 'job_title', 'start_date', 'end_date', 'job_description']
    list_editable = ['company_name', 'job_title', 'start_date', 'end_date', 'job_description']

    def get_user(self, obj):
        return obj.user.username if obj.user else "-"
    get_user.short_description = "User"

# admin.site.register(Experience, ExperienceAdmin)

class EducationAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'institution', 'degree', 'graduation_year', 'field_of_study', 'certification']
    list_editable = ['institution', 'degree', 'graduation_year', 'field_of_study', 'certification']

    def get_user(self, obj):
        return obj.user.username if obj.user else "-"
    get_user.short_description = "User"

# admin.site.register(Education, EducationAdmin)

class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'team_member', 'platform', 'link']
    list_editable = ['team_member', 'platform', 'link']

    def get_user(self, obj):
        return obj.user.username if obj.user else "-"
    get_user.short_description = "User"

# admin.site.register(SocialLink, SocialLinkAdmin)

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'rating', 'testimonial_notes']
    list_editable = ['designation', 'rating', 'testimonial_notes']
admin.site.register(Testimonial, TestimonialAdmin)

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'message', 'phone', 'status']
    list_editable = ['email', 'subject', 'message', 'phone', 'status']
    list_display_links = ['name']  
admin.site.register(ContactUs, ContactUsAdmin)

class AdminFAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer', 'email_id', 'datetime', 'order']
    list_editable = ['answer', 'email_id', 'order']  
    list_display_links = ['question']  
admin.site.register(AdminFAQ, AdminFAQAdmin)

class UserFAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer', 'email_id', 'datetime', 'status']
    list_editable = ['answer', 'email_id', 'status']  
    list_display_links = ['question']  
admin.site.register(UserFAQ, UserFAQAdmin)

class BlogAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'time', 'image', 'subject', 'description', 'slug', 'blog_quotes', 'designation', 'featured']
    list_editable = ['image', 'subject', 'description', 'slug', 'blog_quotes', 'designation', 'featured']  # Removed 'name', 'date', 'time'
    prepopulated_fields ={'slug':('subject',)}
    list_display_links = ['name']  
admin.site.register(Blog, BlogAdmin)

class BlogImageAdmin(admin.ModelAdmin):
    list_display = ['blog', 'image']
    list_editable = ['image']
admin.site.register(BlogImage, BlogImageAdmin)

class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['blog', 'fullname', 'email', 'website', 'comments', 'save_comments']
    list_editable = ['fullname', 'email', 'website', 'comments', 'save_comments'] 
admin.site.register(BlogComment, BlogCommentAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]  # Display all fields dynamically
    list_editable = [field.name for field in Service._meta.fields if field.name not in ['id', 'created_at', 'updated_at']]
    search_fields = [field.name for field in Service._meta.fields if field.name not in ['id', 'created_at', 'updated_at']]
    list_filter = [field.name for field in Service._meta.fields if field.name not in ['id', 'description', 'image', 'logo', 'created_at', 'updated_at']]

admin.site.register(Service, ServiceAdmin)

class ServiceDetailAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceDetail._meta.fields]  # Display all fields dynamically
    list_editable = [field.name for field in ServiceDetail._meta.fields if field.name not in ['id', 'created_at', 'updated_at']]
    search_fields = [field.name for field in ServiceDetail._meta.fields if field.name not in ['id', 'created_at', 'updated_at']]
    list_filter = [field.name for field in ServiceDetail._meta.fields if field.name not in ['id', 'description', 'image', 'created_at', 'updated_at']]

admin.site.register(ServiceDetail, ServiceDetailAdmin)


class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
admin.site.register(NewsletterSubscriber,NewsletterSubscriberAdmin)