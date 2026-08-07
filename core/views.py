from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from .models import *
from .email_utils import notify_welcome
import json, threading


def get_base_ctx():
    s = ChurchSettings.get_settings()
    return {
        'settings':      s,
        'announcements': Announcement.objects.filter(is_active=True)[:5],
        'service_times': ServiceTime.objects.all(),
        'bg_hero':       s.get_bg('hero'),
        'bg_about':      s.get_bg('about'),
        'bg_sermons':    s.get_bg('sermons'),
        'bg_events':     s.get_bg('events'),
        'bg_ministries': s.get_bg('ministries'),
        'bg_testimonies':s.get_bg('testimonies'),
        'bg_give':       s.get_bg('give'),
    }


def home(request):
    ctx = get_base_ctx()
    ctx.update({
        'service_times':   ServiceTime.objects.all(),
        'latest_sermons':  Sermon.objects.all()[:4],
        'upcoming_events': Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5],
        'leadership':      Leadership.objects.all()[:1],
        'ministries':      Ministry.objects.all()[:8],
        'testimonies':     Testimony.objects.filter(is_approved=True)[:10],
        'flyers':          Flyer.objects.filter(is_active=True),
    })
    return render(request, 'core/home.html', ctx)


def sermons(request):
    ctx = get_base_ctx()
    ctx['sermons'] = Sermon.objects.all()
    return render(request, 'core/sermons.html', ctx)


def events(request):
    ctx = get_base_ctx()
    ctx.update({
        'upcoming': Event.objects.filter(date__gte=timezone.now().date()).order_by('date'),
        'past':     Event.objects.filter(date__lt=timezone.now().date()).order_by('-date'),
    })
    return render(request, 'core/events.html', ctx)


def about(request):
    ctx = get_base_ctx()
    ctx.update({'leadership': Leadership.objects.all(), 'ministries': Ministry.objects.all()})
    return render(request, 'core/about.html', ctx)


def give(request):
    ctx = get_base_ctx()
    ctx['payment_methods'] = PaymentMethod.objects.filter(is_active=True)
    return render(request, 'core/give.html', ctx)


def contact(request):
    return render(request, 'core/contact.html', get_base_ctx())


def new_visitor(request):
    ctx = get_base_ctx()
    ctx['service_times'] = ServiceTime.objects.all()
    return render(request, 'core/new_visitor.html', ctx)


def testimonies_page(request):
    """Browse/read testimonies — 10 at a time with load-more."""
    ctx = get_base_ctx()
    ctx['testimonies'] = Testimony.objects.filter(is_approved=True).order_by('-is_featured', '-date')
    return render(request, 'core/testimonies.html', ctx)


def testimony_detail(request, pk):
    """Individual testimony page."""
    ctx = get_base_ctx()
    t = get_object_or_404(Testimony, pk=pk, is_approved=True)
    ctx['testimony'] = t
    ctx['related'] = Testimony.objects.filter(
        is_approved=True, category=t.category
    ).exclude(pk=pk)[:4]
    return render(request, 'core/testimony_detail.html', ctx)


def testimony_submit_page(request):
    """Separate page for submitting a testimony."""
    ctx = get_base_ctx()
    return render(request, 'core/testimony_submit.html', ctx)


def live_page(request):
    ctx = get_base_ctx()
    ctx['upcoming_events'] = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:3]
    return render(request, 'core/live.html', ctx)


@require_POST
def submit_testimony(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 'auth_required': True,
            'message': 'You must be a registered member to submit a testimony.',
            'login_url': '/auth/login/?next=/testimonies/submit/',
        })
    name      = request.POST.get('name', '').strip() or request.user.get_full_name() or request.user.username
    location  = request.POST.get('location', 'Worldwide').strip()
    title     = request.POST.get('title', '').strip()
    testimony = request.POST.get('testimony', '').strip()
    category  = request.POST.get('category', 'General')
    photo_url = request.POST.get('photo_url', '').strip()
    if not testimony:
        return JsonResponse({'success': False, 'message': 'Please write your testimony.'})
    profile = getattr(request.user, 'profile', None)
    obj = Testimony(name=name, location=location, title=title, testimony=testimony,
                    category=category, photo_url=photo_url, member=profile)
    if 'photo_file' in request.FILES:
        obj.photo_file = request.FILES['photo_file']
    elif profile and profile.photo_file:
        obj.photo_file = profile.photo_file
    obj.save()
    return JsonResponse({'success': True, 'message': 'Thank you! Your testimony has been submitted for review.'})


@require_POST
def save_push_subscription(request):
    try:
        data = json.loads(request.body)
        sub_json = json.dumps(data)
        if request.user.is_authenticated:
            profile, _ = MemberProfile.objects.get_or_create(user=request.user)
            profile.push_subscription = sub_json
            profile.save(update_fields=['push_subscription'])
        request.session['push_subscription'] = sub_json
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    ctx = get_base_ctx()
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        phone      = request.POST.get('phone', '').strip()
        password   = request.POST.get('password', '')
        password2  = request.POST.get('password2', '')
        gender     = request.POST.get('gender', '')
        ministry   = request.POST.get('ministry_interest', '')
        if password != password2:
            ctx['error'] = 'Passwords do not match.'
        elif len(password) < 8:
            ctx['error'] = 'Password must be at least 8 characters.'
        elif User.objects.filter(email=email).exists():
            ctx['error'] = 'An account with this email already exists.'
        else:
            try:
                user = User.objects.create_user(
                    username=email, email=email, password=password,
                    first_name=first_name, last_name=last_name)
                MemberProfile.objects.create(user=user, phone=phone, gender=gender, ministry_interest=ministry)
                login(request, user)
                threading.Thread(target=notify_welcome, args=(user, first_name), daemon=True).start()
                return redirect('dashboard')
            except IntegrityError:
                ctx['error'] = 'Account creation failed. Please try again.'
    ctx['ministries'] = Ministry.objects.all()
    return render(request, 'core/register.html', ctx)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    ctx = get_base_ctx()
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect(request.POST.get('next', 'dashboard'))
        ctx['error'] = 'Invalid email or password.'
    ctx['next'] = request.GET.get('next', '')
    return render(request, 'core/login.html', ctx)


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    ctx = get_base_ctx()
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    ctx['profile']         = profile
    ctx['upcoming_events'] = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5]
    ctx['latest_sermons']  = Sermon.objects.all()[:4]
    ctx['latest_notifs']   = NotificationLog.objects.all()[:10]
    return render(request, 'core/dashboard.html', ctx)


@login_required
@require_POST
def update_profile(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    user = request.user
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name  = request.POST.get('last_name',  user.last_name)
    user.save(update_fields=['first_name', 'last_name'])
    profile.phone                = request.POST.get('phone', profile.phone)
    profile.address              = request.POST.get('address', profile.address)
    profile.ministry_interest    = request.POST.get('ministry_interest', profile.ministry_interest)
    profile.notify_events        = 'notify_events'        in request.POST
    profile.notify_sermons       = 'notify_sermons'       in request.POST
    profile.notify_announcements = 'notify_announcements' in request.POST
    if 'photo_file' in request.FILES:
        profile.photo_file = request.FILES['photo_file']
    profile.save()
    return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})
