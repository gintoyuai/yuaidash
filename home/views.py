from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from .models import *
from django.db.models import Q
from .models import NewsletterSubscriber
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

#index
def loadindex(request):
    return render(request,"index.html")

#aboutus
def loadaboutus(request):
    return render(request,"aboutus.html")

#team
def loadteam(request):
    team = Team.objects.filter(status='active')
    return render(request,"team.html",{'team':team})

#teamdetails
def loadteamdetails(request,id):
    teamsingle= get_object_or_404(Team,id=id)
    return render(request,"team-details.html",{'sTeam':teamsingle})

#testimonilas
def loadtestimonial(request):
    testimonial=Testimonial.objects.all()
    return render(request,"testimonial.html",{'test':testimonial})

#faq
def loadfaq(request):
    Faq = AdminFAQ.objects.filter(status='answered')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        question = request.POST.get('question')
        faq=UserFAQ(
            email_id= email,
            question=question
        )
        faq.save()
    return render(request,"faq.html",{'faq':Faq})

#contactus
def loadcontact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        contact_query = ContactUs(
            name=name,
            email=email,
            subject=subject,
            phone=phone,
            message=message
        )
        contact_query.save()
        messages.success(request, 'Your message has been sent successfully. We will get back to you soon!')
        return redirect('loadcontact')
    return render(request, "contact.html")

#services
def loadservice(request):
    services = Service.objects.filter(status='Active') 
    return render(request, "service.html", {'services': services}) 


#servicesdetails
def loadservicedetails(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service_details = ServiceDetail.objects.filter(service=service, status='active')
    services = Service.objects.filter(status='Active')  # Fetch all active services

    return render(request, 'service-details.html', {
        'service': service,
        'service_details': service_details,
        'services': services  # Pass this to template
    })


#bloggrid
def loadbloggrid(request):
    return render(request,"blog-grid.html")

#blog-details
def loadblog(request):
    Blogs=Blog.objects.all()
    return render(request,"blog-2column.html",{'blogList':Blogs})

def Searching(request):
    if 'q' in request.GET:
        query=request.GET.get('q')  #to store data in search box

        blogLi=Blog.objects.all().filter(Q(name__icontains=query)|Q(description__icontains=query))
    return render(request,'search.html',{'searchBlog':blogLi})

def loadblogdetails(request,Bslug):
    detailBlog = get_object_or_404(Blog, slug=Bslug)

    if request.method == 'POST':
        
        name = request.POST.get('Name')
        email = request.POST.get('Email')
        website = request.POST.get('WebSite')
        message = request.POST.get('Message')

        blog_comment = BlogComment(
            blog=detailBlog,  
            fullname=name,
            email=email,
            website=website,
            comments=message
        )
        blog_comment.save()
        
        messages.success(request, "Comment posted successfully!")
        return redirect('loadblogdetails', Bslug=Bslug)
       

    cmt = BlogComment.objects.filter(blog=detailBlog,save_comments=True)
    blogde = BlogImage.objects.filter(blog=detailBlog)
    return render(request, 'blog-details.html', {'dbList': detailBlog, 'cmt': cmt,'blogimg':blogde})




def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            if not NewsletterSubscriber.objects.filter(email=email).exists():
                NewsletterSubscriber.objects.create(email=email)
                return JsonResponse({"message": "Thank you for subscribing!", "success": True})
            else:
                return JsonResponse({"message": "This email is already subscribed.", "success": False})
        else:
            return JsonResponse({"message": "Invalid email address!", "success": False})
    
    return JsonResponse({"message": "Invalid request!", "success": False})




@csrf_exempt
def contact_us_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            contact = ContactUs.objects.create(
                name=data['name'],
                email=data['email'],
                subject=data['subject'],
                message=data['message'],
                phone=data.get('phone', '')
            )
            return JsonResponse({'status': 'success', 'message': 'Your message has been sent successfully. We will get back to you soon!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
