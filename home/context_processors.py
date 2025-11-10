from home.views import *


def testimonials(request):
    testimonial=Testimonial.objects.all()
    return {'test':testimonial}


def services(request):
    services = Service.objects.all()  
    return {'services': services} 


def blogs(request):
    Blogs=Blog.objects.all()
    return {'blogList':Blogs}


