from datetime import date, timedelta, timezone
import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg, Count

from django.conf import settings
from .models import *
from home.models import *

# Add pages
def add_blog(request):
    if request.method == 'POST':      
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        blog_quotes = request.POST.get('blog_quotes', '')
        designation = request.POST.get('designation', '')
        featured = 'featured' in request.POST
        
        blog = Blog(
            name=name,
            subject=subject,
            description=description,
            blog_quotes=blog_quotes,
            designation=designation,
            featured=featured
        )

        if 'image' in request.FILES:
            blog.image = request.FILES['image']
    
        blog.save()

        if 'blog_images' in request.FILES:
            files = request.FILES.getlist('blog_images')
            for file in files:
                BlogImage.objects.create(blog=blog, image=file)
        
        messages.success(request, 'Blog added successfully!')
        return redirect('blog')  
    return render(request, 'dashboard/add-blog.html')


def edit_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    existing_images = blog.blog_images.all()
    
    if request.method == 'POST':
        # Update blog fields
        blog.name = request.POST.get('name')
        blog.subject = request.POST.get('subject')
        blog.description = request.POST.get('description')
        blog.blog_quotes = request.POST.get('blog_quotes', '')
        blog.designation = request.POST.get('designation', '')
        blog.featured = 'featured' in request.POST
        
        # Handle featured image update
        if 'image' in request.FILES:
            blog.image = request.FILES['image']
        
        blog.save()
        
        # Handle additional images
        if 'blog_images' in request.FILES:
            files = request.FILES.getlist('blog_images')
            for file in files:
                BlogImage.objects.create(blog=blog, image=file)

        #  Handle image deletions
        images_to_delete = request.POST.getlist('delete_images')
        if images_to_delete:
            for img_id in images_to_delete:
                try:
                    img = BlogImage.objects.get(id=img_id, blog=blog)
                    img.image.delete(save=False)  # remove file from storage
                    img.delete()  # remove from DB
                except BlogImage.DoesNotExist:
                    pass

        
        messages.success(request, 'Blog updated successfully!')
        return redirect('blog')
    
    return render(request, 'dashboard/edit-blog.html', {'blog': blog ,'existing_images': existing_images})



def delete_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    blog.delete()
    messages.success(request, 'Blog deleted successfully!')
    return redirect('blog')   



def add_faq(request):
    if request.method == "POST":
        question = request.POST.get('question')
        answer = request.POST.get('answer', '')
        email_id = request.POST.get('email_id')
        order = request.POST.get('order', 0)
        status = request.POST.get('status', 'unanswered')

        # Validate required fields
        if not all([question, email_id]):
            messages.error(request, "Question and Email are required fields.")
            return redirect('add_faq')

        # Validate email
        try:
            validate_email(email_id)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect('add_faq')

        # Validate order
        try:
            order = int(order)
        except (ValueError, TypeError):
            order = 0

        # Normalize status
        if status not in ['unanswered', 'answered']:
            status = 'unanswered'

        if answer and status == 'unanswered':
            status = 'answered'
        elif not answer and status == 'answered':
            status = 'unanswered'
        try:
            AdminFAQ.objects.create(
                question=question,
                answer=answer,
                email_id=email_id,
                order=order,
                status=status
            )
            messages.success(request, "FAQ added successfully!")
            return redirect('faq')
        except Exception as e:
            messages.error(request, f"Error saving FAQ: {e}")
            return redirect('add_faq')

    return render(request, 'dashboard/add-faq.html')

def edit_faq(request, faq_id):
    faq = get_object_or_404(AdminFAQ, id=faq_id)

    if request.method == "POST":
        try:
            question = request.POST.get('question')
            answer = request.POST.get('answer', '')
            email_id = request.POST.get('email_id')
            order = request.POST.get('order', 0)
            status = request.POST.get('status', 'unanswered')

            if not all([question, email_id]):
                messages.error(request, "Question and Email are required fields.")
                return redirect('edit_faq', faq_id=faq_id)

            try:
                validate_email(email_id)
            except ValidationError:
                messages.error(request, "Please enter a valid email address.")
                return redirect('edit_faq', faq_id=faq_id)

            faq.question = question
            faq.answer = answer
            faq.email_id = email_id
            faq.order = int(order) if order else 0
            faq.status = status if status in ['unanswered', 'answered'] else 'unanswered'
            faq.save()

            messages.success(request, "FAQ updated successfully!")
            return redirect('faq')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('edit_faq', faq_id=faq_id)

    context = {'faq': faq}
    return render(request, 'dashboard/edit-faq.html', context)


def delete_faq(request, faq_id):
    faq = get_object_or_404(AdminFAQ, id=faq_id)
    faq.delete()
    messages.success(request, "FAQ deleted successfully!")
    return redirect('faq')



def add_services(request):
    if request.method == 'POST':
        try:
            service_name = request.POST.get('service_name')
            description = request.POST.get('description')
            status = request.POST.get('status', 'Active')

            if not service_name:
                messages.error(request, 'Service name is required')
                return redirect('add_service')

            service = Service(
                service=service_name,
                description=description,
                status=status
            )

            if 'logo' in request.FILES:
                service.logo = request.FILES['logo']
            if 'image' in request.FILES:
                service.image = request.FILES['image']

            service.save()

            messages.success(request, f'Service "{service_name}" created successfully!')
            return redirect('services')

        except Exception as e:
            messages.error(request, f'Error creating service: {str(e)}')
            return redirect('add_service')

    return render(request, 'dashboard/add-services.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            next_url = request.GET.get('next', 'yuaidash')  
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'dashboard/logindash.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                service_name = request.POST.get('service_name', '').strip()
                description = request.POST.get('description', '').strip()
                status = request.POST.get('status', 'Active')

                if not service_name:
                    messages.error(request, 'Service name is required')
                    return redirect('edit_service', pk=service.id)

                service.service = service_name
                service.description = description
                service.status = status

                if 'logo' in request.FILES and request.FILES['logo']:
                    service.logo = request.FILES['logo']
                if request.POST.get('remove_logo') == '1':
                    if service.logo:
                        service.logo.delete(save=False)
                        service.logo = None

                if 'image' in request.FILES and request.FILES['image']:
                    service.image = request.FILES['image']
                if request.POST.get('remove_image') == '1':
                    if service.image:
                        service.image.delete(save=False)
                        service.image = None

                service.save()

                messages.success(request, f'Service "{service.service}" updated successfully!')
                return redirect('services')

        except Exception as e:
            messages.error(request, f'Error updating service: {str(e)}')
            return redirect('edit_service', pk=service.id)

    return render(request, 'dashboard/edit-services.html', {
        'service': service,
    })
    
    

def add_service_details(request, service_id):
    service = get_object_or_404(Service, pk=service_id)

    if request.method == 'POST':
        try:
            detail_titles = request.POST.getlist('detail_titles[]')
            detail_statuses = request.POST.getlist('detail_statuses[]')
            detail_descriptions = request.POST.getlist('detail_descriptions[]')
            detail_images = request.FILES.getlist('detail_images[]')

            for i, title in enumerate(detail_titles):
                if not title.strip():
                    continue

                sd = ServiceDetail(
                    service=service,
                    title=title.strip(),
                    description=detail_descriptions[i] if i < len(detail_descriptions) else '',
                    status=detail_statuses[i] if i < len(detail_statuses) else 'active'
                )

                if i < len(detail_images) and detail_images[i]:
                    sd.image = detail_images[i]

                sd.save()

            messages.success(request, 'Service details added successfully!')
            return redirect('service_detail', service_id=service.id)

        except Exception as e:
            messages.error(request, f'Error adding details: {str(e)}')
            return redirect('service_detail', service_id=service.id)

    # 👇 GET request → render form
    return render(request, 'dashboard/add-servicedetails.html', {
        'service': service
    })


def edit_service_detail(request, detail_id):
    service_detail = get_object_or_404(ServiceDetail, pk=detail_id)
    service = service_detail.service

    if request.method == 'POST':
        try:
            with transaction.atomic():
                title = request.POST.get('detail_title')
                status = request.POST.get('detail_status')
                description = request.POST.get('detail_description')

                # Update fields
                service_detail.title = title or service_detail.title
                service_detail.description = description or service_detail.description
                service_detail.status = status or service_detail.status

                if 'detail_image' in request.FILES:
                    if service_detail.image:
                        service_detail.image.delete(save=False)
                    service_detail.image = request.FILES['detail_image']

                if request.POST.get('remove_detail_image') == '1':
                    if service_detail.image:
                        service_detail.image.delete(save=False)
                        service_detail.image = None

                service_detail.save()
                messages.success(request, 'Service detail updated successfully!')
                return redirect('service_detail', service_id=service.id)

        except Exception as e:
            messages.error(request, f'Error updating detail: {str(e)}')
            return redirect('edit_service_detail', detail_id=detail_id)

    return render(request, 'dashboard/edit-service-details.html', {
        'service': service,
        'service_detail': service_detail
    })

def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    try:
        service.delete()
        messages.success(request, "Service deleted successfully.")
        return redirect('services')
    except Exception as e:
        messages.error(request, f"Failed to delete service: {e}")
        return redirect('edit_service', pk=pk)


@login_required
def delete_service_detail(request, pk):
    detail = get_object_or_404(ServiceDetail, pk=pk)
    service_pk = detail.service_id

    if request.method == 'POST':
        try:
            if detail.image:
                detail.image.delete(save=False)
            detail.delete()
            messages.success(request, "Detail deleted successfully.")
        except Exception as e:
            messages.error(request, f"Failed to delete detail: {e}")
        return redirect('service_detail', service_id=service_pk)

    messages.error(request, "Invalid request method.")
    return redirect('service_detail', service_id=service_pk)


def add_team(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            role = request.POST.get('role')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            skills = request.POST.get('skills')
            experience_years = request.POST.get('experience_years')
            current_project = request.POST.get('current_project')
            portfolio = request.POST.get('portfolio')
            status = request.POST.get('status', 'active')

            if not all([name, role, email, phone_number, skills, experience_years]):
                messages.error(request, "All required fields must be filled.")
                return redirect('add_team')

            if Team.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('add_team')

            if Team.objects.filter(phone_number=phone_number).exists():
                messages.error(request, "Phone number already exists.")
                return redirect('add_team')

            team_member = Team(
                name=name,
                role=role,
                email=email,
                phone_number=phone_number,
                skills=skills,
                experience_years=experience_years,
                current_project=current_project,
                portfolio=portfolio,
                status=status
            )
            if 'photo' in request.FILES:
                team_member.photo = request.FILES['photo']
            if 'cv' in request.FILES:
                team_member.cv = request.FILES['cv']

            team_member.save()
            degrees = request.POST.getlist('degree[]')
            institutions = request.POST.getlist('institution[]')
            graduation_years = request.POST.getlist('graduation_year[]')
            fields_of_study = request.POST.getlist('field_of_study[]')
            certifications = request.POST.getlist('certification[]')

            for i in range(len(degrees)):
                if degrees[i] and institutions[i]:
                    Education.objects.create(
                        team=team_member,
                        degree=degrees[i],
                        institution=institutions[i],
                        graduation_year=graduation_years[i] if i < len(graduation_years) and graduation_years[i] else None,
                        field_of_study=fields_of_study[i] if i < len(fields_of_study) else '',
                        certification=certifications[i] if i < len(certifications) else ''
                    )

            # Experience
            company_names = request.POST.getlist('company_name[]')
            job_titles = request.POST.getlist('job_title[]')
            start_dates = request.POST.getlist('start_date[]')
            end_dates = request.POST.getlist('end_date[]')
            job_descriptions = request.POST.getlist('job_description[]')

            for i in range(len(company_names)):
                if company_names[i] and job_titles[i]:
                    Experience.objects.create(
                        team=team_member,
                        company_name=company_names[i],
                        job_title=job_titles[i],
                        start_date=start_dates[i] if i < len(start_dates) and start_dates[i] else None,
                        end_date=end_dates[i] if i < len(end_dates) and end_dates[i] else None,
                        job_description=job_descriptions[i] if i < len(job_descriptions) else ''
                    )

            # Social Links
            platforms = request.POST.getlist('platform[]')
            links = request.POST.getlist('link[]')

            for i in range(len(platforms)):
                if platforms[i] and links[i]:
                    if not SocialLink.objects.filter(team_member=team_member, platform=platforms[i]).exists():
                        SocialLink.objects.create(
                            team_member=team_member,
                            platform=platforms[i],
                            link=links[i]
                        )

            messages.success(request, "Team member added successfully!")
            return redirect('team')  

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('add_team')
    return render(request, 'dashboard/add-team.html')

def edit_team(request, pk):
    member = get_object_or_404(Team, pk=pk)
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                name = request.POST.get('name', '').strip()
                role = request.POST.get('role', '').strip()
                email = request.POST.get('email', '').strip()
                phone_number = request.POST.get('phone_number', '').strip()
                skills = request.POST.get('skills', '').strip()
                experience_years = request.POST.get('experience_years') or member.experience_years
                current_project = request.POST.get('current_project', '').strip()
                portfolio = request.POST.get('portfolio', '').strip()
                status = request.POST.get('status', member.status)

                if not all([name, role, email, phone_number, skills, str(experience_years)]):
                    messages.error(request, "All required fields must be filled.")
                    return redirect('edit_team', pk=member.id)

                if Team.objects.exclude(pk=member.id).filter(email=email).exists():
                    messages.error(request, "Email already exists.")
                    return redirect('edit_team', pk=member.id)

                if Team.objects.exclude(pk=member.id).filter(phone_number=phone_number).exists():
                    messages.error(request, "Phone number already exists.")
                    return redirect('edit_team', pk=member.id)
                member.name = name
                member.role = role
                member.email = email
                member.phone_number = phone_number
                member.skills = skills
                try:
                    member.experience_years = int(experience_years)
                except Exception:
                    # keep existing if invalid
                    pass
                member.current_project = current_project
                member.portfolio = portfolio
                member.status = status

                if 'photo' in request.FILES and request.FILES['photo']:
                    # delete old file to avoid orphan
                    if getattr(member, 'photo', None):
                        try:
                            member.photo.delete(save=False)
                        except Exception:
                            pass
                    member.photo = request.FILES['photo']
                if request.POST.get('remove_photo') == '1':
                    if getattr(member, 'photo', None):
                        try:
                            member.photo.delete(save=False)
                        except Exception:
                            pass
                        member.photo = None

                if 'cv' in request.FILES and request.FILES['cv']:
                    if getattr(member, 'cv', None):
                        try:
                            member.cv.delete(save=False)
                        except Exception:
                            pass
                    member.cv = request.FILES['cv']
                if request.POST.get('remove_cv') == '1':
                    if getattr(member, 'cv', None):
                        try:
                            member.cv.delete(save=False)
                        except Exception:
                            pass
                        member.cv = None

                member.save()

                existing_edu_ids = request.POST.getlist('edu_ids[]')  # hidden inputs in template
                existing_degrees = request.POST.getlist('edu_degree[]')
                existing_institutions = request.POST.getlist('edu_institution[]')
                existing_years = request.POST.getlist('edu_year[]')
                existing_fields = request.POST.getlist('edu_field[]')
                existing_certs = request.POST.getlist('edu_cert[]')

                for i, eid in enumerate(existing_edu_ids):
                    if not eid:
                        continue
                    try:
                        edu = Education.objects.get(pk=int(eid), team=member)
                    except (Education.DoesNotExist, ValueError):
                        continue

                    edu.degree = existing_degrees[i] if i < len(existing_degrees) else edu.degree
                    edu.institution = existing_institutions[i] if i < len(existing_institutions) else edu.institution
                    if i < len(existing_years) and existing_years[i]:
                        try:
                            edu.graduation_year = int(existing_years[i])
                        except Exception:
                            pass
                    edu.field_of_study = existing_fields[i] if i < len(existing_fields) else edu.field_of_study
                    edu.certification = existing_certs[i] if i < len(existing_certs) else edu.certification
                    edu.save()

                new_degrees = request.POST.getlist('new_degree[]')
                new_institutions = request.POST.getlist('new_institution[]')
                new_years = request.POST.getlist('new_year[]')
                new_fields = request.POST.getlist('new_field[]')
                new_certs = request.POST.getlist('new_cert[]')

                for i in range(len(new_degrees)):
                    deg = new_degrees[i].strip() if i < len(new_degrees) else ''
                    if not deg:
                        continue
                    Education.objects.create(
                        team=member,
                        degree=deg,
                        institution=new_institutions[i].strip() if i < len(new_institutions) else '',
                        graduation_year=int(new_years[i]) if i < len(new_years) and new_years[i] else None,
                        field_of_study=new_fields[i].strip() if i < len(new_fields) else '',
                        certification=new_certs[i].strip() if i < len(new_certs) else ''
                    )

                existing_exp_ids = request.POST.getlist('exp_ids[]')
                existing_companies = request.POST.getlist('exp_company[]')
                existing_titles = request.POST.getlist('exp_title[]')
                existing_starts = request.POST.getlist('exp_start[]')
                existing_ends = request.POST.getlist('exp_end[]')
                existing_descs = request.POST.getlist('exp_desc[]')

                for i, eid in enumerate(existing_exp_ids):
                    if not eid:
                        continue
                    try:
                        ex = Experience.objects.get(pk=int(eid), team=member)
                    except (Experience.DoesNotExist, ValueError):
                        continue

                    ex.company_name = existing_companies[i] if i < len(existing_companies) else ex.company_name
                    ex.job_title = existing_titles[i] if i < len(existing_titles) else ex.job_title
                    ex.start_date = existing_starts[i] if i < len(existing_starts) and existing_starts[i] else ex.start_date
                    ex.end_date = existing_ends[i] if i < len(existing_ends) and existing_ends[i] else ex.end_date
                    ex.job_description = existing_descs[i] if i < len(existing_descs) else ex.job_description
                    ex.save()

                new_companies = request.POST.getlist('new_company[]')
                new_titles = request.POST.getlist('new_job_title[]')
                new_starts = request.POST.getlist('new_start[]')
                new_ends = request.POST.getlist('new_end[]')
                new_descs = request.POST.getlist('new_job_desc[]')

                for i in range(len(new_companies)):
                    comp = new_companies[i].strip() if i < len(new_companies) else ''
                    if not comp:
                        continue
                    Experience.objects.create(
                        team=member,
                        company_name=comp,
                        job_title=new_titles[i].strip() if i < len(new_titles) else '',
                        start_date=new_starts[i] if i < len(new_starts) and new_starts[i] else None,
                        end_date=new_ends[i] if i < len(new_ends) and new_ends[i] else None,
                        job_description=new_descs[i].strip() if i < len(new_descs) else ''
                    )

                existing_social_ids = request.POST.getlist('social_ids[]')
                existing_platforms = request.POST.getlist('social_platform[]')
                existing_links = request.POST.getlist('social_link[]')

                for i, sid in enumerate(existing_social_ids):
                    if not sid:
                        continue
                    try:
                        s = SocialLink.objects.get(pk=int(sid), team_member=member)
                    except (SocialLink.DoesNotExist, ValueError):
                        continue

                    s.platform = existing_platforms[i] if i < len(existing_platforms) else s.platform
                    s.link = existing_links[i] if i < len(existing_links) else s.link
                    s.save()

                new_platforms = request.POST.getlist('new_platform[]')
                new_links = request.POST.getlist('new_link[]')

                for i in range(len(new_platforms)):
                    pl = new_platforms[i].strip() if i < len(new_platforms) else ''
                    lk = new_links[i].strip() if i < len(new_links) else ''
                    if not pl or not lk:
                        continue
                    if not SocialLink.objects.filter(team_member=member, platform=pl, link=lk).exists():
                        SocialLink.objects.create(team_member=member, platform=pl, link=lk)

                messages.success(request, "Team member updated successfully!")
                return redirect('team')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('edit_team', pk=member.id)

    return render(request, 'dashboard/edit-team.html', {'member': member})

@require_POST
def delete_team(request, pk):
    """
    Hard delete a Team member and cleanup files.
    Simple POST-only endpoint (triggered by small form in template).
    """
    member = get_object_or_404(Team, pk=pk)

    # TODO: permission checks if needed
    try:
        with transaction.atomic():
            # delete related files: photo, cv
            if getattr(member, 'photo', None):
                try:
                    member.photo.delete(save=False)
                except Exception:
                    pass
            if getattr(member, 'cv', None):
                try:
                    member.cv.delete(save=False)
                except Exception:
                    pass

            # delete the member (cascade deletes related rows)
            member.delete()
            messages.success(request, "Team member deleted.")
            return redirect('team')
    except Exception as e:
        messages.error(request, f"Failed to delete member: {e}")
        return redirect('edit_team', pk=pk)

@require_POST
def delete_education(request, pk):
    edu = get_object_or_404(Education, pk=pk)
    member_pk = edu.team_id
    try:
        edu.delete()
        messages.success(request, "Education entry deleted.")
    except Exception as e:
        messages.error(request, f"Failed to delete education entry: {e}")
    return redirect('edit_team', pk=member_pk)


@require_POST
def delete_experience(request, pk):
    ex = get_object_or_404(Experience, pk=pk)
    member_pk = ex.team_id
    try:
        ex.delete()
        messages.success(request, "Experience entry deleted.")
    except Exception as e:
        messages.error(request, f"Failed to delete experience entry: {e}")
    return redirect('edit_team', pk=member_pk)


@require_POST
def delete_sociallink(request, pk):
    s = get_object_or_404(SocialLink, pk=pk)
    member_pk = s.team_member_id
    try:
        s.delete()
        messages.success(request, "Social link deleted.")
    except Exception as e:
        messages.error(request, f"Failed to delete social link: {e}")
    return redirect('edit_team', pk=member_pk)



def add_testimonial(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            designation = request.POST.get('designation')
            rating = request.POST.get('rating', 5)
            testimonial_notes = request.POST.get('testimonial_notes')

            if not all([name, designation, testimonial_notes]):
                messages.error(request, "All required fields must be filled.")
                return redirect('add_testimonial')
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    rating = 5  
            except (ValueError, TypeError):
                rating = 5  

            testimonial = Testimonial(
                name=name,
                designation=designation,
                rating=rating,
                testimonial_notes=testimonial_notes
            )
            if 'photo' in request.FILES:
                testimonial.photo = request.FILES['photo']
            testimonial.save()
            messages.success(request, "Testimonial added successfully!")
            return redirect('testimonial')  
        
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('add_testimonial') 
             
    return render(request, 'dashboard/add-testimonial.html')

def edit_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            designation = request.POST.get('designation')
            rating = request.POST.get('rating', 5)
            testimonial_notes = request.POST.get('testimonial_notes')

            if not all([name, designation, testimonial_notes]):
                messages.error(request, "All required fields must be filled.")
                return redirect('edit_testimonial', testimonial_id=testimonial_id)
            
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    rating = 5  
            except (ValueError, TypeError):
                rating = 5  

            # Update testimonial fields
            testimonial.name = name
            testimonial.designation = designation
            testimonial.rating = rating
            testimonial.testimonial_notes = testimonial_notes
            
            # Handle photo update
            if 'photo' in request.FILES:
                testimonial.photo = request.FILES['photo']
                
            testimonial.save()
            messages.success(request, "Testimonial updated successfully!")
            return redirect('testimonial')  
        
        except Exception as e:
            messages.error(request, f"Error updating testimonial: {str(e)}")
            return redirect('edit_testimonial', testimonial_id=testimonial_id)
    
    # Pre-fill form with existing data
    context = {
        'testimonial': testimonial,
        'edit_mode': True
    }
    return render(request, 'dashboard/edit-testimonial.html', context)

def delete_testimonial(request, testimonial_id):
    if request.method == "POST":
        try:
            testimonial = get_object_or_404(Testimonial, id=testimonial_id)
            testimonial.delete()
            messages.success(request, "Testimonial deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting testimonial: {str(e)}")
    
    return redirect('testimonial')




def yuaidash(request):
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    traffic_data = []
    for day in last_7_days:
        count = Traffic.objects.filter(timestamp__date=day).count()
        traffic_data.append({"date": day.strftime("%b %d"), "count": count})

    team_count = Team.objects.count()
    testimonial_count = Testimonial.objects.count()
    faq_count = UserFAQ.objects.count()
    blog_count = Blog.objects.count()
    queries_co = ContactUs.objects.count()
    services_co = Service.objects.count()
    NewsletterSub_count = NewsletterSubscriber.objects.count()

    context = {
        'team_count': team_count,
        'testimonial_count': testimonial_count,
        'faq_count': faq_count,
        'blog_count': blog_count,
        'queries_co': queries_co,
        'services_co': services_co,
        'NewsletterSub_count': NewsletterSub_count,
        "traffic_today": Traffic.objects.filter(timestamp__date=today).count(),
        "total_visits": Traffic.objects.count(),
        "traffic_labels": [d["date"] for d in traffic_data],
        "traffic_counts": [d["count"] for d in traffic_data],
    }
    return render(request, 'dashboard/yuaidash.html', context)


def blog(request):
    blog_obj = Blog.objects.all().annotate(comment_count=Count('blog_comments')).order_by('-date', '-time')

    total_blogs = blog_obj.count()
    featured_count = blog_obj.filter(featured=True).count()
    non_featured_count = total_blogs - featured_count
    total_comments = BlogComment.objects.count()

    paginator = Paginator(blog_obj, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_blogs': total_blogs,
        'featured_count': featured_count,
        'non_featured_count': non_featured_count,
        'total_comments': total_comments,
    }

    return render(request, 'dashboard/blog.html', context)


def blog_detail(request, blog_id):
  
    try:
        blog = get_object_or_404(Blog, id=blog_id)
        
        context = {
            'blog': blog,
        }
        
        return render(request, 'dashboard/detail-blog.html', context)
        
    except Blog.DoesNotExist:
        raise Http404("Blog post not found")
    
@csrf_exempt
def toggle_save_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(BlogComment, id=comment_id)
        comment.save_comments = not comment.save_comments
        comment.save()
        return JsonResponse({
            'status': 'success',
            'save_comments': comment.save_comments
        })
    return JsonResponse({'status': 'error'}, status=400)

def faq_request(request):
    userfaq_obj = UserFAQ.objects.all()
    context = {'userfaq_obj': userfaq_obj}  
    return render(request, 'dashboard/faq-request.html',context)

def faq(request):
    faq_obj = AdminFAQ.objects.all().order_by('-id')
    total_faq = faq_obj.count()
    
    paginator = Paginator(faq_obj, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,   
        'total_faq': total_faq, 
    }
    return render(request, 'dashboard/faq.html', context)


def queries(request):
    queries_obj = ContactUs.objects.all()
    context = {'queries_obj': queries_obj}  
    return render(request, 'dashboard/queries.html', context)

def ref(request):
    return render(request, 'dashboard/ref.html')

def services(request):
    Service_obj = Service.objects.all().order_by('-id')
    total_services = Service_obj.count()
    total_active = Service_obj.filter(status='Active').count()
    total_inactive = Service_obj.filter(status='Inactive').count()

    paginator = Paginator(Service_obj, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,               
        'total_services': total_services,   
        'total_active': total_active,       
        'total_inactive': total_inactive,   
    }
    return render(request, 'dashboard/services.html', context)



def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service_details = ServiceDetail.objects.filter(service=service)
    related_services = Service.objects.filter(status='Active').exclude(id=service_id)[:4]   
    context = {
        'service': service,
        'service_details': service_details,
        'related_services': related_services,
    }
        
    return render(request, 'dashboard/detail-service.html', context)

def team(request):
    team_obj = Team.objects.all()
    context = {'team_obj': team_obj}
    return render(request, 'dashboard/team.html', context)


def team_detail(request, team_id):
    team_member = get_object_or_404(Team, id=team_id)
    education = team_member.education.all()
    experience = team_member.experience.all()
    social_links = team_member.social_links.all()
    
    context = {
        'team_member': team_member,
        'education': education,
        'experience': experience,
        'social_links': social_links,
    }
    return render(request, 'dashboard/detail-team.html', context)





def testimonial(request):
    testimonial_obj = Testimonial.objects.all().order_by('-id')  
    
    testimonial_count = testimonial_obj.count()
    average_rating = testimonial_obj.aggregate(Avg('rating'))['rating__avg'] or 0

    paginator = Paginator(testimonial_obj, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,  # paginated data
        'testimonial_count': testimonial_count,
        'average_rating': round(average_rating, 2),
    }

    return render(request, 'dashboard/testimonial.html', context)

from django.core.paginator import Paginator

def newsletter(request):
    newsletter_obj = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
    total_count = newsletter_obj.count()
    active_count = newsletter_obj.filter(status='active').count()
    inactive_count = newsletter_obj.filter(status='inactive').count()

    paginator = Paginator(newsletter_obj, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    campaigns = Campaign.objects.all().order_by('-created_at')


    context = {
        'newsletter_obj': page_obj,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'campaigns': campaigns,
    }
    return render(request, 'dashboard/newsletter.html', context)


import csv

def add_subscriber(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.warning(request, 'This email is already subscribed!')
        else:
            NewsletterSubscriber.objects.create(email=email)
            messages.success(request, 'Subscriber added successfully!')
    
    return redirect('newsletter')

def toggle_subscriber(request, subscriber_id):
    if request.method == 'POST':
        subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
        
        # Toggle status
        if subscriber.status == 'active':
            subscriber.status = 'inactive'
            action = 'deactivated'
        else:
            subscriber.status = 'active'
            action = 'activated'
        
        subscriber.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'new_status': subscriber.status,
                'message': f'Subscriber {action} successfully'
            })
        
        messages.success(request, f'Subscriber {action} successfully')
        return redirect('newsletter')  # Replace with your actual view name
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def delete_subscriber(request, subscriber_id):
    """
    Delete a subscriber permanently
    """
    if request.method == 'POST':
        subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
        email = subscriber.email
        
        subscriber.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Subscriber {email} deleted successfully'
            })
        
        messages.success(request, f'Subscriber {email} deleted successfully')
        return redirect('newsletter')  # Replace with your actual view name
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def export_subscribers(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribers_{}.csv"'.format(
        timezone.now().strftime('%Y%m%d_%H%M')
    )
    writer = csv.writer(response)
    writer.writerow(['Email', 'Subscribed At', 'Status'])
    subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
    for subscriber in subscribers:
        status_map = {
            'active': 'Active',
            'inactive': 'Inactive'
        }
        status = status_map.get(subscriber.status, 'Unknown')
        
        writer.writerow([
            subscriber.email, 
            subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M'), 
            status
        ]) 
    return response

def create_campaign(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        subject = request.POST.get('subject', '').strip()
        content = request.POST.get('content', '').strip()
        status = request.POST.get('status', 'draft')
        scheduled_at = request.POST.get('scheduled_at')

        if not name or not subject or not content:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('newsletter')
                
        schedule_time = None
        if scheduled_at:
            try:
                schedule_time = datetime.strptime(scheduled_at, '%Y-%m-%dT%H:%M')
            except ValueError:
                messages.error(request, 'Invalid date/time format for schedule.')
                return redirect('newsletter')

        Campaign.objects.create(
            name=name,
            subject=subject,
            content=content,
            status=status,
            scheduled_at=schedule_time
        )

        messages.success(request, f'Campaign "{name}" created successfully!')
    return redirect('newsletter')

from django.core.mail import EmailMultiAlternatives

def send_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if campaign.status == 'sent':
        messages.warning(request, 'This campaign has already been sent!')
        return redirect('newsletter')
    
    active_subscribers = NewsletterSubscriber.objects.filter(status='active')
    if not active_subscribers.exists():
        messages.warning(request, 'No active subscribers to send this campaign to.')
        return redirect('newsletter')

    sent_count = 0
    failed_emails = []

    for subscriber in active_subscribers:
        try:
            email = EmailMultiAlternatives(
                subject=campaign.subject,
                body=campaign.content,  # plain text fallback
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            email.attach_alternative(campaign.content, "text/html")  # HTML content
            email.send(fail_silently=False)
            sent_count += 1
        except Exception as e:
            failed_emails.append(subscriber.email)
            print(f"Failed to send to {subscriber.email}: {str(e)}")

    campaign.status = 'sent'
    campaign.sent_at = timezone.now()
    campaign.save()

    # Display results
    if failed_emails:
        messages.warning(request, f'Campaign sent to {sent_count} subscribers. Failed for {len(failed_emails)} emails.')
    else:
        messages.success(request, f'Campaign sent successfully to {sent_count} subscribers!')

    return redirect('newsletter')


def delete_campaign(request, campaign_id):
    """Delete a campaign"""
    campaign = get_object_or_404(Campaign, id=campaign_id)
    campaign.delete()
    messages.success(request, 'Campaign deleted successfully!')
    return redirect('newsletter_dashboard')



# //email faq:

def send_faq_response(request):
    if request.method == 'POST':
        faq_id = request.POST.get('faq_id')
        response_text = request.POST.get('response_text')
        
        # Get the FAQ object
        faq = get_object_or_404(UserFAQ, id=faq_id)
        
        # Update the FAQ with answer and status
        faq.answer = response_text
        faq.status = 'answered'
        faq.save()
        
        # Send email
        subject = f"Response to your FAQ: {faq.question[:50]}..."
        message = f"""
        Dear User,
        
        Thank you for your question: "{faq.question}"
        
        Here is our response:
        {response_text}
        
        Best regards,
        Support Team
        """
        
        try:
            send_mail(
                subject,
                message,
                None,  # Uses DEFAULT_FROM_EMAIL from settings
                [faq.email_id],
                fail_silently=False,
            )
            messages.success(request, 'Response sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending email: {str(e)}')
        
        return redirect('faq_request')
    
    return redirect('faq_request')