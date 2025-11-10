from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.
#TEAM MEMBERS DETAILS
class Team(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='team_photos/', blank=True, null=True)
    skills = models.TextField()
    experience_years = models.IntegerField()
    current_project = models.CharField(max_length=255, blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    cv = models.FileField(upload_to='team_cvs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name
#EDUCATIONAL QUALIFICATIONS OF TEAM MEMBERS
    
class Education(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    graduation_year = models.IntegerField()
    field_of_study = models.CharField(max_length=255)
    certification = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} - {self.team.name}"
#EXPERIENCES OF TEAM MEMBERS
class Experience(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='experience')
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # Can be null if the person is currently employed
    job_description = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company_name} - {self.team.name}"
    
#social links of team members

class SocialLink(models.Model):
    SOCIAL_PLATFORMS = [
        ('GitHub', 'GitHub'),
        ('LinkedIn', 'LinkedIn'),
        ('Instagram', 'Instagram'),
        ('Twitter', 'Twitter'),
        ('Facebook', 'Facebook'),
        ('Other', 'Other'),
    ]

    id = models.AutoField(primary_key=True)  # Explicitly defining ID (not necessary, but you can)
    team_member = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="social_links")
    platform = models.CharField(max_length=100, choices=SOCIAL_PLATFORMS)
    link = models.URLField(unique=True)

    class Meta:
        unique_together = ('team_member', 'platform')  # Ensures no duplicate platform per team member

    def __str__(self):
        return f"{self.team_member.name} - {self.platform}"

#create testimonial model
class Testimonial(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    rating = models.IntegerField(default=5)  # Rating out of 5
    testimonial_notes = models.TextField()
    photo = models.ImageField(upload_to='test_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.designation}"
    
#create model for contact us
class ContactUs(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.subject} - {self.name}"

class AdminFAQ(models.Model):
    STATUS_CHOICES = [
        ('unanswered', 'Unanswered'),
        ('answered', 'Answered'),
    ]

    id = models.AutoField(primary_key=True)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)  
    email_id = models.EmailField()
    datetime = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unanswered')

    def __str__(self):
        return f"Q: {self.question[:50]}..."  

class UserFAQ(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)  
    email_id = models.EmailField()
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('unanswered', 'Unanswered'), ('answered', 'Answered')],
        default='unanswered'
    )

    def __str__(self):
        return f"Q: {self.question[:50]}..."  # Show first 50 chars of the question

class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    blog_quotes = models.TextField(blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject
    
    def get_url(self):
        return reverse('loadblogdetails',args=[self.slug])

class BlogImage(models.Model):
    id = models.AutoField(primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_images')
    image = models.ImageField(upload_to='blog_extra_images/')

    def __str__(self):
        return f"Image for {self.blog.name}"
    

class BlogComment(models.Model):
    id = models.AutoField(primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_comments')
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    comments = models.TextField()
    save_comments = models.BooleanField(default=False)  # Checkbox for saving comments

    def __str__(self):
        return f"Comment by {self.fullname} on {self.blog.name}"


class Service(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    service = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='services/images/', blank=True, null=True)
    logo = models.ImageField(upload_to='services/logos/', blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service
#create service_details table
    
class ServiceDetail(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]

    service = models.ForeignKey('Service', on_delete=models.CASCADE)  # Foreign key to Services table
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return self.email