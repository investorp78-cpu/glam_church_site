from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib import messages as adm_msg
from .models import *
from .email_utils import notify_new_event, notify_new_announcement
import threading

admin.site.site_header  = "✦ Gospel Life Apostolic Family Assembly — Admin Panel"
admin.site.site_title   = "GLAFA Admin"
admin.site.index_title  = "Welcome to the Gospel Life Apostolic Family Assembly Dashboard"


# ── Church Settings ──────────────────────────────────────────
@admin.register(ChurchSettings)
class ChurchSettingsAdmin(admin.ModelAdmin):

    def _img_help(self):
        return mark_safe(
            '<div style="margin:8px 0;padding:12px 14px;background:rgba(192,24,42,.06);'
            'border:1px solid rgba(192,24,42,.2);border-radius:8px;">'
            '<p style="font-size:.72rem;font-weight:700;color:#e8edf8;margin:0 0 8px;">'
            '&#128205; Upload your image to one of these services, copy the direct URL, paste in the URL field:</p>'
            '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;">'
            '<a href="https://imgbb.com" target="_blank" style="background:#c0182a;color:#fff;'
            'padding:6px 12px;border-radius:6px;font-size:.7rem;font-weight:700;text-decoration:none;">'
            '&#128247; ImgBB</a>'
            '<a href="https://console.cloudinary.com/console/media_library" target="_blank" '
            'style="background:#3448c5;color:#fff;padding:6px 12px;border-radius:6px;'
            'font-size:.7rem;font-weight:700;text-decoration:none;">&#9729; Cloudinary</a>'
            '<a href="https://drive.google.com" target="_blank" style="background:#1a73e8;color:#fff;'
            'padding:6px 12px;border-radius:6px;font-size:.7rem;font-weight:700;text-decoration:none;">'
            '&#128193; Google Drive</a>'
            '</div>'
            '<small style="color:#7a8aaa;font-size:.63rem;line-height:1.6;display:block;">'
            '<b style="color:#e8edf8;">ImgBB:</b> Upload image &#8594; copy "Direct link" &nbsp;|&nbsp;'
            '<b style="color:#e8edf8;">Cloudinary:</b> Upload &#8594; click image &#8594; copy URL &nbsp;|&nbsp;'
            '<b style="color:#e8edf8;">Google Drive:</b> Upload &#8594; Share (Anyone with link) &#8594; '
            'change URL to: drive.google.com/uc?export=view&amp;id=YOUR_FILE_ID'
            '</small></div>'
        )

    def get_fieldsets(self, request, obj=None):
        h = self._img_help()
        return [
            ('&#127968; Church Identity', {
                'description': 'Basic info shown across the entire website.',
                'fields': ('church_name', 'tagline', 'denomination', 'founding_year')
            }),
            ('&#128444; Church Logo', {
                'description': h,
                'fields': ('logo_url', 'logo_file')
            }),
            ('&#128214; Mission & Vision', {
                'fields': ('mission_statement', 'vision_statement')
            }),
            ('&#128221; Hero Bible Verse', {
                'description': 'Shown on the homepage hero section.',
                'fields': ('hero_bible_verse', 'hero_bible_text')
            }),
            ('&#128250; Livestream', {
                'description': 'Paste your YouTube embed URL. Tick "Live right now?" during active services.',
                'fields': ('livestream_embed_url', 'livestream_channel_url', 'is_live_now')
            }),
            ('&#128222; Contact Information', {
                'fields': ('address', 'phone_primary', 'phone_secondary', 'whatsapp', 'email')
            }),
            ('&#128241; Social Media Links', {
                'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'twitter_url')
            }),
            ('&#128506; Google Maps', {
                'description': 'Paste the full &lt;iframe&gt; embed code from Google Maps.',
                'fields': ('google_maps_embed',)
            }),
            ('&#128444; Hero Background — Homepage', {'description': h, 'fields': ('bg_hero_url', 'bg_hero_file')}),
            ('&#128444; About Section Image',         {'description': h, 'fields': ('bg_about_url', 'bg_about_file')}),
            ('&#128444; Sermons Background',          {'description': h, 'fields': ('bg_sermons_url', 'bg_sermons_file')}),
            ('&#128444; Events Background',           {'description': h, 'fields': ('bg_events_url', 'bg_events_file')}),
            ('&#128444; Ministries Background',       {'description': h, 'fields': ('bg_ministries_url', 'bg_ministries_file')}),
            ('&#128444; Testimonies Background',      {'description': h, 'fields': ('bg_testimonies_url', 'bg_testimonies_file')}),
            ('&#128444; Give / CTA Banner',           {'description': h, 'fields': ('bg_give_url', 'bg_give_file')}),
        ]

    def has_add_permission(self, request):
        return not ChurchSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ServiceTime)
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display  = ['service_name', 'day', 'start_time', 'end_time', 'description', 'order']
    list_editable = ['order']
    ordering      = ['order', 'day']


# ── Leadership / Pastors ──────────────────────────────────────
@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display  = ['name', 'title', 'is_senior_pastor', 'order', '_photo']
    list_editable = ['order', 'is_senior_pastor']

    def _photo(self, obj):
        url = obj.photo_file.url if obj.photo_file else obj.photo_url
        if url:
            return format_html('<img src="{}" style="height:40px;width:40px;border-radius:50%;object-fit:cover;"/>', url)
        return '—'
    _photo.short_description = 'Photo'


# ── Ministries ────────────────────────────────────────────────
@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'icon_class', 'leader_name', 'meeting_time', 'order', '_bg']
    list_editable = ['order', 'icon_class']

    def _bg(self, obj):
        url = obj.get_bg()
        if url:
            return format_html('<img src="{}" style="height:32px;width:56px;object-fit:cover;border-radius:4px;"/>', url)
        return '—'
    _bg.short_description = 'Card BG'


# ── Payment Methods ───────────────────────────────────────────
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display  = ['label', 'method_type', 'bank_name', 'account_number', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter   = ['method_type', 'is_active']
    fieldsets = (
        ('Method Info',  {'fields': ('method_type', 'label', 'icon_class', 'is_active', 'order')}),
        ('Bank Details', {'fields': ('bank_name', 'account_name', 'account_number')}),
        ('Online / USSD',{'fields': ('api_public_key', 'ussd_code')}),
        ('Giving Types', {
            'description': 'Comma-separated list e.g. Tithe,Offering,Building Fund',
            'fields': ('giving_types',)
        }),
    )


# ── Sermons ───────────────────────────────────────────────────
@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display   = ['title', 'preacher', 'date', 'bible_passage', 'is_featured']
    list_editable  = ['is_featured']
    list_filter    = ['is_featured']
    search_fields  = ['title', 'preacher']
    date_hierarchy = 'date'


# ── Events (with auto-email on save) ─────────────────────────
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ['title', 'date', 'location', 'is_featured', 'send_notification', '_img']
    list_editable = ['is_featured', 'send_notification']
    list_filter   = ['is_featured', 'send_notification']
    search_fields = ['title', 'location']
    actions       = ['send_email_now']

    def _img(self, obj):
        url = obj.get_image()
        if url:
            return format_html('<img src="{}" style="height:32px;width:56px;object-fit:cover;border-radius:4px;"/>', url)
        return '—'
    _img.short_description = 'Image'

    def save_model(self, request, obj, form, change):
        is_new = not obj.pk
        super().save_model(request, obj, form, change)
        if obj.send_notification and is_new:
            threading.Thread(target=notify_new_event, args=(obj,), daemon=True).start()
            self.message_user(request, f"✉️ Email notification queued for '{obj.title}'.", adm_msg.SUCCESS)

    @admin.action(description='📧 Send email notification to all subscribed members')
    def send_email_now(self, request, queryset):
        for event in queryset:
            threading.Thread(target=notify_new_event, args=(event,), daemon=True).start()
        self.message_user(request, f"✉️ Emails queued for {queryset.count()} event(s).", adm_msg.SUCCESS)


# ── Announcements (with auto-email on save) ───────────────────
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ['title', 'date_posted', 'is_active', 'is_urgent', 'send_notification']
    list_editable = ['is_active', 'is_urgent', 'send_notification']
    list_filter   = ['is_active', 'is_urgent']
    actions       = ['send_email_now']

    def save_model(self, request, obj, form, change):
        is_new = not obj.pk
        super().save_model(request, obj, form, change)
        if obj.send_notification and is_new:
            threading.Thread(target=notify_new_announcement, args=(obj,), daemon=True).start()
            self.message_user(request, f"✉️ Announcement email queued for '{obj.title}'.", adm_msg.SUCCESS)

    @admin.action(description='📧 Send email notification to all subscribed members')
    def send_email_now(self, request, queryset):
        for ann in queryset:
            threading.Thread(target=notify_new_announcement, args=(ann,), daemon=True).start()
        self.message_user(request, f"✉️ Emails queued for {queryset.count()} announcement(s).", adm_msg.SUCCESS)


# ── Flyers / Posters ──────────────────────────────────────────
@admin.register(Flyer)
class FlyerAdmin(admin.ModelAdmin):
    list_display  = ['title', 'is_active', 'order', 'date_posted', '_preview', 'link_url']
    list_editable = ['is_active', 'order']
    list_filter   = ['is_active']
    search_fields = ['title', 'caption']
    readonly_fields = ['date_posted', '_preview']
    fieldsets = (
        ('Flyer Details', {'fields': ('title', 'caption', 'is_active', 'order')}),
        ('📸 Image', {
            'description': '⚡ RECOMMENDED: Upload file (saved to Cloudinary permanently) OR paste a Cloudinary/image URL below.',
            'description': '📌 Go to imgbb.com → upload → copy Direct link → paste in Image URL field below.',
            'fields': ('image_url', 'image_file', '_preview'),
        }),
        ('🔗 Click-through Link (optional)', {'fields': ('link_url',)}),
        ('Info', {'fields': ('date_posted',)}),
    )

    def _preview(self, obj):
        url = obj.get_image()
        if url:
            return format_html('<img src="{}" style="height:120px;max-width:200px;object-fit:cover;border-radius:6px;border:1px solid rgba(0,0,0,.1);"/>', url)
        return "No image uploaded yet."
    _preview.short_description = "Image Preview"


# ── Testimonies ───────────────────────────────────────────────
@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'title', 'category', 'date', 'is_approved', 'is_featured', '_photo']
    list_editable = ['is_approved', 'is_featured']
    list_filter   = ['is_approved', 'is_featured', 'category']
    search_fields = ['name', 'testimony', 'location']
    readonly_fields = ['date', '_photo']
    fieldsets = (
        ('✍️ Testimony Content', {
            'description': 'Fill in the testimony details below. Tick "Approved" to make it visible on the website.',
            'fields': ('name', 'location', 'category', 'title', 'testimony'),
        }),
        ('📸 Photo', {
            'description': 'Upload a photo OR paste a URL. Leave blank to use the member initials.',
            'fields': ('photo_file', 'photo_url', '_photo'),
        }),
        ('✅ Status', {
            'fields': ('is_approved', 'is_featured', 'date'),
        }),
        ('👤 Member Link (auto-set)', {
            'classes': ('collapse',),
            'fields': ('member',),
        }),
    )

    def _photo(self, obj):
        url = obj.photo_file.url if obj.photo_file else obj.photo_url
        if url:
            return format_html('<img src="{}" style="height:60px;width:60px;border-radius:50%;object-fit:cover;border:2px solid #eee;"/>', url)
        return '— No photo'
    _photo.short_description = 'Photo Preview'


# ── Member Profiles ───────────────────────────────────────────
@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'membership_status', 'phone', 'notify_events', 'notify_announcements', 'date_registered']
    list_filter   = ['membership_status', 'notify_events', 'notify_announcements']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    readonly_fields = ['date_registered']
    actions       = ['send_welcome_email_action']

    @admin.action(description='📧 Send welcome email to selected members')
    def send_welcome_email_action(self, request, queryset):
        from .email_utils import notify_welcome
        for profile in queryset:
            threading.Thread(target=notify_welcome, args=(profile.user, profile.user.first_name or profile.user.username), daemon=True).start()
        self.message_user(request, f"✉️ Welcome emails queued for {queryset.count()} member(s).", adm_msg.SUCCESS)


# ── Notification Log ──────────────────────────────────────────
@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display    = ['title', 'notif_type', 'sent_at', 'sent_count']
    list_filter     = ['notif_type']
    readonly_fields = ['sent_at', 'sent_count', 'title', 'body', 'notif_type']

    def has_add_permission(self, request):
        return False
