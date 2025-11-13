from .models import *
from home.models import *
from datetime import date, timedelta

from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
        
        messages.success(request, 'Blog updated successfully!')
        return redirect('blog')
    
    return render(request, 'dashboard/edit-blog.html', {'blog': blog})



def delete_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog deleted successfully!')
        return redirect('blog')
    
    return render(request, 'confirm_delete.html', {'blog': blog})




def add_faq(request):
    if request.method == "POST":
        try:
            question = request.POST.get('question')
            answer = request.POST.get('answer', '')
            email_id = request.POST.get('email_id')
            order = request.POST.get('order', 0)
            status = request.POST.get('status', 'unanswered')

            if not all([question, email_id]):
                messages.error(request, "Question and Email are required fields.")
                return redirect('add_faq')

            try:
                validate_email(email_id)
            except ValidationError:
                messages.error(request, "Please enter a valid email address.")
                return redirect('add_faq')

            try:
                order = int(order)
            except (ValueError, TypeError):
                order = 0

            if status not in ['unanswered', 'answered']:
                status = 'unanswered'

            if answer and status == 'unanswered':
                status = 'answered'
            elif not answer and status == 'answered':
                status = 'unanswered'

            faq = AdminFAQ(
                question=question,
                answer=answer,
                email_id=email_id,
                order=order,
                status=status
            )

            faq.save()

            messages.success(request, "FAQ added successfully!")
            return redirect('faq_list')  

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('add_faq')
    return render(request, 'dashboard/add-faq.html')

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


def edit_service_details(request, service_id):
    service_detail = get_object_or_404(ServiceDetail, pk=service_id)
    service = service_detail.service

    if request.method == 'POST':
        try:
            with transaction.atomic():
                title = request.POST.get('detail_title')
                status = request.POST.get('detail_status')
                description = request.POST.get('detail_description')
                
                should_delete = request.POST.get('delete_detail') == '1'
                
                if should_delete:
                    service_detail.delete()
                    messages.success(request, 'Service detail deleted successfully!')
                    return redirect('edit_service', pk=service.id)
                else:
                    service_detail.title = title if title else service_detail.title
                    service_detail.description = description if description else service_detail.description
                    service_detail.status = status if status else service_detail.status

                    if 'detail_image' in request.FILES and request.FILES['detail_image']:
                        if service_detail.image:
                            service_detail.image.delete(save=False)
                        service_detail.image = request.FILES['detail_image']

                    if request.POST.get('remove_detail_image') == '1':
                        if service_detail.image:
                            service_detail.image.delete(save=False)
                            service_detail.image = None

                    service_detail.save()
                    messages.success(request, 'Service detail updated successfully!')
                    
                    return redirect('edit_service_details', service_id=service_detail.id)

        except Exception as e:
            messages.error(request, f'Error updating detail: {str(e)}')
            return redirect('edit_service_details', service_id=service_detail.id)
    return render(request, 'dashboard/edit-service-details.html', {
        'service': service,
        'service_detail': service_detail  # Single detail object
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

@require_POST
def delete_service_detail(request, pk):
    detail = get_object_or_404(ServiceDetail, pk=pk)
    service_pk = detail.service_id

    try:
      
        if getattr(detail, 'image', None):
            try:
                detail.image.delete(save=False)
            except Exception:
                pass

        detail.delete()
        messages.success(request, "Detail deleted.")
        return redirect('edit_service', pk=service_pk)
    except Exception as e:
        messages.error(request, f"Failed to delete detail: {e}")
        return redirect('edit_service', pk=service_pk)


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
    blog_obj = Blog.objects.all()
    context = {'blog_obj': blog_obj}
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



def faq_request(request):
    # Base queryset
    userfaq_queryset = UserFAQ.objects.all()
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Apply status filter
    if status_filter == 'unanswered_requests':
        userfaq_queryset = userfaq_queryset.filter(status='unanswered')
    elif status_filter == 'answered_requests':
        userfaq_queryset = userfaq_queryset.filter(status='answered')
    
    # Apply date filter
    if date_filter == 'today':
        today = timezone.now().date()
        userfaq_queryset = userfaq_queryset.filter(datetime__date=today)
    elif date_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        userfaq_queryset = userfaq_queryset.filter(datetime__gte=week_ago)
    elif date_filter == 'month':
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        userfaq_queryset = userfaq_queryset.filter(datetime__gte=month_start)
    
    # Apply search filter
    if search_query:
        userfaq_queryset = userfaq_queryset.filter(
            Q(question__icontains=search_query) | Q(email_id__icontains=search_query)
        )
    
    # Order by datetime (newest first)
    userfaq_queryset = userfaq_queryset.order_by('-datetime')
    
    # PAGINATION
    paginator = Paginator(userfaq_queryset, 12)  # items per page
    page_number = request.GET.get('page', 1)

    try:
        userfaq_obj = paginator.page(page_number)
    except PageNotAnInteger:
        userfaq_obj = paginator.page(1)
    except EmptyPage:
        userfaq_obj = paginator.page(paginator.num_pages)
    
    # Calculate statistics
    total_requests = UserFAQ.objects.count()
    unanswered_requests = UserFAQ.objects.filter(status='unanswered').count()
    answered_requests = UserFAQ.objects.filter(status='answered').count()
    
    context = {
        'userfaq_obj': userfaq_obj,
        'total_requests': total_requests,
        'unanswered_requests': unanswered_requests,
        'answered_requests': answered_requests,
    }
    
    return render(request, 'dashboard/faq-request.html', context)


def faq(request):
    faq_obj = AdminFAQ.objects.all()
    context = {'faq_obj': faq_obj}  
    return render(request, 'dashboard/faq.html', context)

def queries(request):
    #Base Queryset
    queries_obj = ContactUs.objects.all()
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Apply status filter
    if status_filter == 'pending_queries':
        queries_obj = queries_obj.filter(status='pending')
    elif status_filter == 'resolved_queries':
        queries_obj = queries_obj.filter(status='resolved')
        
    # date filter CURRENTLY NOT POSSIBLE because datetime field is not in ContactUs model
    
    # if date_filter == 'today':
    #     today = timezone.now().date()
    #     queries_obj = queries_obj.filter(datetime__date=today)
    # elif date_filter == 'week':
    #     week_ago = timezone.now() - timedelta(days=7)
    #     queries_obj = queries_obj.filter(datetime__gte=week_ago)
    # elif date_filter == 'month':
    #     month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    #     queries_obj = queries_obj.filter(datetime__gte=month_start)
    
    # Apply search filter
    if search_query:
        queries_obj = queries_obj.filter(
            Q(subject__icontains=search_query) | 
            Q(message__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query)
         ) 
        
    # Order by id (newest first)
    queries_obj = queries_obj.order_by('-id')
    
    # PAGINATION
    
    paginator = Paginator(queries_obj, 12)  # items per page
    page_number = request.GET.get('page', 1)

    try:
        queries_obj = paginator.page(page_number)
    except PageNotAnInteger:
        queries_obj = paginator.page(1)
    except EmptyPage:
        queries_obj = paginator.page(paginator.num_pages)
    
    #Calculate statistics
    total_queries = ContactUs.objects.count()
    pending_queries = ContactUs.objects.filter(status='pending').count()
    resolved_queries = ContactUs.objects.filter(status='resolved').count()
    
    context = {
        'queries_obj': queries_obj,
        'total_queries':total_queries,
        'pending_queries':pending_queries,
        'resolved_queries':resolved_queries,
        }  
    return render(request, 'dashboard/queries.html', context)


def send_query_response(request):
    """Handle sending email response to contact query"""
    if request.method == 'POST':
        query_id = request.POST.get('query_id')
        response_text = request.POST.get('response_text')
        
        # Get the query
        query = get_object_or_404(ContactUs, id=query_id)
        
        # Send email to user
        subject = f"Re: {query.subject}"
        message = f"""
Dear {query.name},

Thank you for contacting us regarding: "{query.subject}"

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
                [query.email],
                fail_silently=False,
            )
            
            # Update status to resolved
            query.status = 'resolved'
            query.save()
            
            messages.success(request, f'Response sent successfully to {query.email}')
        except Exception as e:
            messages.error(request, f'Failed to send response: {str(e)}')
        
        return redirect('queries')
    
    return redirect('queries')


def mark_query_resolved(request, query_id):
    """Mark a query as resolved without sending email"""
    query = get_object_or_404(ContactUs, id=query_id)
    query.status = 'resolved'
    query.save()
    messages.success(request, 'Query marked as resolved')
    return redirect('queries')

import csv  # Add this at the top if not present

def export_queries_csv(request):
    """Export all contact queries to CSV file"""
    
    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact_queries.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Subject', 'Message', 'Status', 'Date'])
    
    # Get all ContactUs objects from database
    queries = ContactUs.objects.all().order_by('-id')
    
    # Write each query as a row
    for query in queries:
        writer.writerow([
            query.id,
            query.name,
            query.email,
            query.phone if query.phone else '',  # Show empty if no phone
            query.subject,
            query.message,
            query.status,
            'N/A'  # Date field not available in ContactUs model
        ])
    
    # Return the CSV file
    return response


def ref(request):
    return render(request, 'dashboard/ref.html')

def services(request):
    Service_obj = Service.objects.all()
    context = {'Service_obj': Service_obj
          }
    return render(request, 'dashboard/services.html' , context)

def service_detail(request, service_id):

    service = get_object_or_404(Service, id=service_id)
    service_details = ServiceDetail.objects.filter(service=service, status='active')
    related_services = Service.objects.filter(status='Active').exclude(id=service_id)[:4]
    
    context = {
        'service': service,
        'service_details': service_details,
        'related_services': related_services,
    }
        
    return render(request, 'dashboard/detail-service.html', context)

def team(request):
    """Display team members with filtering and pagination (12 per page)"""
    
    # Start with all team members
    team_list = Team.objects.all()
    
    # Get filter parameters from URL query string
    role_filter = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort_by = request.GET.get('sort', '-id')
    
    # Apply role filter if provided
    if role_filter:
        team_list = team_list.filter(role=role_filter)
    
    # Apply status filter if provided
    if status_filter:
        team_list = team_list.filter(status=status_filter)
    
    # Apply sorting with validation (prevent SQL injection)
    allowed_sort_fields = [
        'name', '-name',
        'role', '-role',
        'id', '-id',
        'experience_years', '-experience_years'
    ]
    
    if sort_by in allowed_sort_fields:
        team_list = team_list.order_by(sort_by)
    else:
        team_list = team_list.order_by('-id')  # Default: newest first
    
    # Extract unique roles for dropdown
    roles = Team.objects.values_list('role', flat=True).distinct().order_by('role')
    
    # Create paginator 
    paginator = Paginator(team_list, 2)
    page_number = request.GET.get('page', 1)
    try:
        team_list = paginator.page(page_number)
    except PageNotAnInteger:
        team_list = paginator.page(1)
    except EmptyPage:
        team_list = paginator.page(paginator.num_pages)
    
    context = {
        'team_obj': team_list,
        'roles': roles,
    }
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
    testimonial_obj = Testimonial.objects.all()
    context = {'testimonial_obj': testimonial_obj}
    return render(request, 'dashboard/testimonial.html',context)

def newsletter(request):
    newsletter_obj = NewsletterSubscriber.objects.all()
    context = {'newsletter_obj': newsletter_obj}
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
    """Activate/Deactivate subscriber"""
    subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
    subscriber.is_active = not subscriber.is_active
    subscriber.save()
    
    status = "activated" if subscriber.is_active else "deactivated"
    messages.success(request, f'Subscriber {status} successfully!')
    return redirect('newsletter_dashboard')

def delete_subscriber(request, subscriber_id):
    """Delete a subscriber"""
    subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
    subscriber.delete()
    messages.success(request, 'Subscriber deleted successfully!')
    return redirect('newsletter_dashboard')

def export_subscribers(request):
    """Export subscribers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Email', 'Subscribed At', 'Status'])
    
    subscribers = NewsletterSubscriber.objects.all()
    for subscriber in subscribers:
        status = 'Active' if subscriber.is_active else 'Inactive'
        writer.writerow([
            subscriber.email, 
            subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M'), 
            status
        ])
    
    return response

def create_campaign(request):
    """Create a new campaign"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        Campaign.objects.create(subject=subject, message=message)
        messages.success(request, 'Campaign created successfully!')
    
    return redirect('newsletter_dashboard')

def send_campaign(request, campaign_id):
    """Send campaign to all active subscribers"""
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    if campaign.is_sent:
        messages.warning(request, 'This campaign has already been sent!')
        return redirect('newsletter_dashboard')
    
    # Get active subscribers
    active_subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    
    # Send email to each subscriber
    sent_count = 0
    for subscriber in active_subscribers:
        try:
            send_mail(
                subject=campaign.subject,
                message=campaign.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send to {subscriber.email}: {str(e)}")
    
    # Update campaign status
    campaign.is_sent = True
    campaign.sent_at = timezone.now()
    campaign.save()
    
    messages.success(request, f'Campaign sent successfully to {sent_count} subscribers!')
    return redirect('newsletter_dashboard')

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


def add_to_faq(request, userfaq_id):
    """Convert a UserFAQ entry to AdminFAQ"""
    if request.method == 'POST':
        # Get the UserFAQ object
        userfaq = get_object_or_404(UserFAQ, id=userfaq_id)

        # Check if this UserFAQ has already been added to AdminFAQ
        existing_faq = AdminFAQ.objects.filter(
            question=userfaq.question,
            email_id=userfaq.email_id
        ).exists()

        if existing_faq:
            messages.warning(request, 'This question has already been added to the FAQ list.')
            return redirect('faq_request')

        # Create new AdminFAQ from UserFAQ
        admin_faq = AdminFAQ(
            question=userfaq.question,
            answer=userfaq.answer if userfaq.answer else '',
            email_id=userfaq.email_id,
            status=userfaq.status,
            order=0  # Default order
        )

        admin_faq.save()

        messages.success(request, 'FAQ added to public FAQ list successfully!')
        return redirect('faq_request')

    return redirect('faq_request')



def export_faq_csv(request):
    """Export all FAQ requests to CSV file"""
    
    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="faq_requests.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['ID', 'Question', 'Email', 'Answer', 'Status', 'Date Submitted'])
    
    # Get all UserFAQ objects from database
    faq_requests = UserFAQ.objects.all().order_by('-datetime')
    
    # Write each FAQ request as a row
    for faq in faq_requests:
        writer.writerow([
            faq.id,
            faq.question,
            faq.email_id,
            faq.answer if faq.answer else '',  # Show empty if no answer
            faq.status,
            faq.datetime.strftime('%d-%m-%Y %H:%M')  # Format: 15-01-2024 14:30
        ])
    
    # Return the CSV file
    return response
