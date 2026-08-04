from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import MemberProfile, NotificationLog

def get_subscribed(field): return MemberProfile.objects.filter(**{field:True}).select_related('user')

def _church(): 
    from .models import ChurchSettings
    try: return ChurchSettings.get_settings().church_name
    except: return "Our Church"

def _site(): return "http://127.0.0.1:8000"

def _header(church, title, subtitle=""):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0c0c0e;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;background:#0c0c0e;">
<tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#111115;border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">
<tr><td style="background:linear-gradient(135deg,#c0182a,#7c0f1a);padding:32px 40px;text-align:center;">
<p style="color:rgba(255,255,255,0.7);font-size:11px;letter-spacing:3px;text-transform:uppercase;margin:0 0 8px;">{church}</p>
<h1 style="color:#fff;font-size:26px;margin:0;font-weight:700;">{title}</h1>
{f'<p style="color:rgba(255,255,255,0.6);font-size:13px;margin:8px 0 0;">{subtitle}</p>' if subtitle else ''}
</td></tr><tr><td style="padding:36px 40px;">"""

def _footer(church, site):
    return f"""</td></tr>
<tr><td style="background:#0c0c0e;padding:20px 40px;text-align:center;border-top:1px solid rgba(255,255,255,0.06);">
<p style="color:#50505e;font-size:12px;margin:0;">You received this as a registered member of {church}.</p>
<p style="color:#50505e;font-size:12px;margin:6px 0 0;"><a href="{site}/dashboard/" style="color:#c0182a;">Manage preferences</a> · <a href="{site}/" style="color:#c0182a;">{site}</a></p>
</td></tr></table></td></tr></table></body></html>"""

def send_bulk(subject, html, text, emails, ntype, ntitle):
    from_email = getattr(settings,'DEFAULT_FROM_EMAIL','church@example.com')
    sent = 0
    for email in emails:
        try:
            msg = EmailMultiAlternatives(subject, text, from_email, [email])
            msg.attach_alternative(html, "text/html")
            msg.send(); sent += 1
        except Exception as e: print(f"[EMAIL ERR] {email}: {e}")
    if ntitle: NotificationLog.objects.create(title=ntitle,body=text[:400],notif_type=ntype,sent_count=sent)
    return sent

def notify_new_event(event):
    members = get_subscribed('notify_events')
    if not members.exists(): return 0
    church = _church(); site = _site()
    date_str = event.date.strftime('%A, %d %B %Y')
    time_str = event.time.strftime('%I:%M %p') if event.time else ''
    html = _header(church,"New Event Announced") + f"""
<h2 style="color:#f5f0e8;font-size:22px;margin:0 0 6px;">{event.title}</h2>
<p style="color:#c0182a;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin:0 0 20px;font-weight:700;">📅 {date_str}{' at '+time_str if time_str else ''}</p>
<p style="color:#7a7a88;font-size:14px;line-height:1.7;margin:0 0 20px;">{event.description[:400]}</p>
<table style="background:#18181e;border-radius:6px;padding:20px;width:100%;margin-bottom:24px;"><tr><td style="color:#7a7a88;font-size:12px;padding:5px 0;">
<span style="color:#c0182a;margin-right:6px;">📍</span><strong style="color:#f5f0e8;">Location:</strong> {event.location}</td></tr>
{'<tr><td style="color:#7a7a88;font-size:12px;padding:5px 0;"><span style="color:#c0182a;margin-right:6px;">⏰</span><strong style="color:#f5f0e8;">Time:</strong> '+time_str+'</td></tr>' if time_str else ''}
</table>
<a href="{site}/events/" style="display:inline-block;background:#c0182a;color:#fff;padding:14px 28px;border-radius:4px;text-decoration:none;font-weight:700;font-size:14px;">View Event →</a>
""" + _footer(church, site)
    text = f"{church} — New Event\n\n{event.title}\n{date_str}\n\n{event.description}\n\nLocation: {event.location}\n\n{site}/events/"
    emails = [m.user.email for m in members if m.user.email]
    return send_bulk(f"📅 New Event: {event.title} — {church}", html, text, emails, 'event', event.title)

def notify_new_announcement(ann):
    members = get_subscribed('notify_announcements')
    if not members.exists(): return 0
    church = _church(); site = _site()
    html = _header(church, "🔴 Urgent Announcement" if ann.is_urgent else "📢 Announcement") + f"""
<h2 style="color:#f5f0e8;font-size:20px;margin:0 0 16px;">{ann.title}</h2>
<p style="color:#7a7a88;font-size:14px;line-height:1.8;margin:0 0 28px;">{ann.body}</p>
<a href="{site}/" style="display:inline-block;background:#c0182a;color:#fff;padding:14px 28px;border-radius:4px;text-decoration:none;font-weight:700;font-size:14px;">Visit Website →</a>
""" + _footer(church, site)
    text = f"{church}\n\n{ann.title}\n\n{ann.body}\n\n{site}/"
    emails = [m.user.email for m in members if m.user.email]
    return send_bulk(f"{'🔴 URGENT: ' if ann.is_urgent else '📢 '}{ann.title}", html, text, emails, 'announcement', ann.title)

def notify_welcome(user, first_name):
    church = _church(); site = _site()
    html = _header(church,"Welcome to the Family! 🙏") + f"""
<h2 style="color:#f5f0e8;font-size:20px;margin:0 0 16px;">Dear {first_name},</h2>
<p style="color:#7a7a88;font-size:14px;line-height:1.8;margin:0 0 16px;">We are so glad you joined the {church} online community! You will now receive updates about events, announcements, and sermons directly to your inbox.</p>
<a href="{site}/dashboard/" style="display:inline-block;background:#c0182a;color:#fff;padding:14px 28px;border-radius:4px;text-decoration:none;font-weight:700;font-size:14px;">Visit My Dashboard →</a>
<p style="color:#50505e;font-size:13px;margin:28px 0 0;">God bless you!<br><strong style="color:#f5f0e8;">— The {church} Team</strong></p>
""" + _footer(church, site)
    text = f"Welcome to {church}, {first_name}!\n\nVisit your dashboard: {site}/dashboard/"
    try:
        from_email = getattr(settings,'DEFAULT_FROM_EMAIL','church@example.com')
        msg = EmailMultiAlternatives(f"Welcome to {church}! 🙏", text, from_email, [user.email])
        msg.attach_alternative(html,"text/html"); msg.send()
    except Exception as e: print(f"[WELCOME EMAIL ERR] {e}")
