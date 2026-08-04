from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class ChurchSettings(models.Model):
    church_name=models.CharField(max_length=200,default="Fountain of Grace Church")
    logo_file=models.ImageField(upload_to='logo/',blank=True,null=True,verbose_name="Church Logo — Upload File",help_text="Upload your church logo PNG/SVG (shown in navbar)")
    logo_url=models.URLField(blank=True,verbose_name="Church Logo — URL",help_text="Or paste a URL to your logo image")
    tagline=models.CharField(max_length=300,default="Where Faith Meets Destiny")
    mission_statement=models.TextField(default="To raise a generation of passionate worshippers who impact their world with the love of Christ.")
    vision_statement=models.TextField(default="A church where every soul finds purpose, every family finds strength, and every community finds transformation.")
    address=models.TextField(default="12 Emmanuel Close, Lekki Phase 1, Lagos, Nigeria")
    phone_primary=models.CharField(max_length=20,default="+234 802 000 0000")
    phone_secondary=models.CharField(max_length=20,blank=True)
    whatsapp=models.CharField(max_length=20,default="+234 802 000 0000")
    email=models.EmailField(default="info@fountainofgrace.org")
    facebook_url=models.URLField(blank=True,default="https://facebook.com")
    instagram_url=models.URLField(blank=True,default="https://instagram.com")
    youtube_url=models.URLField(blank=True,default="https://youtube.com")
    twitter_url=models.URLField(blank=True)
    google_maps_embed=models.TextField(default='<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3964.7286840761937!2d3.4699836750284266!3d6.430620793567657!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x103bf53aec4dd92d%3A0x4a08d6b07ebf2d9f!2sLekki%20Phase%201%2C%20Lagos!5e0!3m2!1sen!2sng!4v1710000000000!5m2!1sen!2sng" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy"></iframe>')
    hero_bible_verse=models.CharField(max_length=200,default="John 10:10")
    hero_bible_text=models.TextField(default="I have come that they may have life, and have it to the full.")
    founding_year=models.CharField(max_length=10,default="1999")
    denomination=models.CharField(max_length=100,default="Pentecostal")
    livestream_embed_url=models.URLField(blank=True,verbose_name="Livestream Embed URL",help_text="e.g. https://www.youtube.com/embed/VIDEOID")
    livestream_channel_url=models.URLField(blank=True,default="https://youtube.com")
    is_live_now=models.BooleanField(default=False,verbose_name="Live right now?")
    bg_hero_file=models.ImageField(upload_to='backgrounds/',blank=True,null=True,verbose_name="Hero BG — Upload")
    bg_hero_url=models.URLField(blank=True,verbose_name="Hero BG — URL",default="https://images.unsplash.com/photo-1604580864964-0462f5d5b1a8?w=1800&q=80")
    bg_about_file=models.ImageField(upload_to='backgrounds/',blank=True,null=True,verbose_name="About BG — Upload")
    bg_about_url=models.URLField(blank=True,verbose_name="About BG — URL")
    bg_sermons_file=models.ImageField(upload_to='backgrounds/',blank=True,null=True,verbose_name="Sermons BG — Upload")
    bg_sermons_url=models.URLField(blank=True,verbose_name="Sermons BG — URL")
    bg_events_file=models.ImageField(upload_to='backgrounds/',blank=True,null=True,verbose_name="Events BG — Upload")
    bg_events_url=models.URLField(blank=True,verbose_name="Events BG — URL",default="https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1400&q=70")
    bg_ministries_file=models.ImageField(upload_to='backgrounds/',blank=True,null=True,verbose_name="Ministries BG — Upload")
    bg_ministries_url=models.URLField(blank=True,verbose_name="Ministries BG — URL")
    bg_testimonies_file=models.ImageField(upload_to='backgrounds/',blank=True,null=True,verbose_name="Testimonies BG — Upload")
    bg_testimonies_url=models.URLField(blank=True,verbose_name="Testimonies BG — URL")
    bg_give_file=models.ImageField(upload_to='backgrounds/',blank=True,null=True,verbose_name="Give CTA BG — Upload")
    bg_give_url=models.URLField(blank=True,verbose_name="Give CTA BG — URL",default="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1400&q=70")
    class Meta: verbose_name="Church Settings"; verbose_name_plural="Church Settings"
    def __str__(self): return self.church_name
    def get_bg(self,section):
        f=getattr(self,f'bg_{section}_file',None); u=getattr(self,f'bg_{section}_url','')
        if f and f.name: return f.url
        return u or ''
    @classmethod
    def get_settings(cls):
        obj,_=cls.objects.get_or_create(pk=1); return obj

class PaymentMethod(models.Model):
    METHOD_CHOICES=[('bank','Bank Transfer'),('paystack','Paystack Online'),('flutterwave','Flutterwave'),('ussd','USSD'),('other','Other')]
    method_type=models.CharField(max_length=20,choices=METHOD_CHOICES,default='bank')
    label=models.CharField(max_length=100)
    bank_name=models.CharField(max_length=100,blank=True)
    account_name=models.CharField(max_length=200,blank=True)
    account_number=models.CharField(max_length=30,blank=True)
    ussd_code=models.CharField(max_length=50,blank=True)
    api_public_key=models.CharField(max_length=200,blank=True,verbose_name="API Public Key")
    icon_class=models.CharField(max_length=50,blank=True,default="fas fa-university")
    giving_types=models.CharField(max_length=300,blank=True,default="Tithe,Offering,Special Seed,Missions,Building Fund")
    is_active=models.BooleanField(default=True)
    order=models.PositiveIntegerField(default=0)
    class Meta: ordering=['order']; verbose_name="Payment Method"; verbose_name_plural="Payment Methods"
    def __str__(self): return self.label
    def giving_type_list(self): return [t.strip() for t in self.giving_types.split(',') if t.strip()]

class ServiceTime(models.Model):
    DAY_CHOICES=[('sunday','Sunday'),('monday','Monday'),('tuesday','Tuesday'),('wednesday','Wednesday'),('thursday','Thursday'),('friday','Friday'),('saturday','Saturday')]
    day=models.CharField(max_length=10,choices=DAY_CHOICES)
    service_name=models.CharField(max_length=100)
    start_time=models.TimeField()
    end_time=models.TimeField(null=True,blank=True)
    description=models.CharField(max_length=200,blank=True)
    order=models.PositiveIntegerField(default=0)
    class Meta: ordering=['order','day','start_time']
    def __str__(self): return f"{self.service_name} — {self.day}"

class Leadership(models.Model):
    name=models.CharField(max_length=200)
    title=models.CharField(max_length=100)
    bio=models.TextField()
    photo_file=models.ImageField(upload_to='leadership/',blank=True,null=True)
    photo_url=models.URLField(blank=True)
    order=models.PositiveIntegerField(default=0)
    is_senior_pastor=models.BooleanField(default=False)
    class Meta: ordering=['order']
    def __str__(self): return f"{self.title} {self.name}"

class Ministry(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    icon_class=models.CharField(max_length=60,default="fas fa-cross",help_text="Font Awesome class e.g. fas fa-fire")
    bg_file=models.ImageField(upload_to='ministries/',blank=True,null=True,verbose_name="Card BG — Upload")
    bg_url=models.URLField(blank=True,verbose_name="Card BG — URL")
    leader_name=models.CharField(max_length=100,blank=True)
    meeting_time=models.CharField(max_length=100,blank=True)
    order=models.PositiveIntegerField(default=0)
    class Meta: ordering=['order']; verbose_name_plural="Ministries"
    def __str__(self): return self.name
    def get_bg(self):
        if self.bg_file and self.bg_file.name: return self.bg_file.url
        return self.bg_url or ''

class Sermon(models.Model):
    title=models.CharField(max_length=200)
    preacher=models.CharField(max_length=100)
    date=models.DateField()
    description=models.TextField(blank=True)
    youtube_url=models.URLField(blank=True)
    audio_url=models.URLField(blank=True)
    bible_passage=models.CharField(max_length=100,blank=True)
    thumbnail_url=models.URLField(blank=True)
    is_featured=models.BooleanField(default=False)
    class Meta: ordering=['-date']
    def __str__(self): return self.title

class Event(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    date=models.DateField()
    end_date=models.DateField(null=True,blank=True)
    time=models.TimeField(null=True,blank=True)
    location=models.CharField(max_length=200,blank=True,default="Church Auditorium")
    image_file=models.ImageField(upload_to='events/',blank=True,null=True,verbose_name="Event Image — Upload")
    image_url=models.URLField(blank=True,verbose_name="Event Image — URL")
    is_featured=models.BooleanField(default=False)
    registration_link=models.URLField(blank=True)
    send_notification=models.BooleanField(default=True,help_text="Email subscribed members when created")
    class Meta: ordering=['date']
    def __str__(self): return self.title
    def is_upcoming(self): return self.date >= timezone.now().date()
    def get_image(self):
        if self.image_file and self.image_file.name: return self.image_file.url
        return self.image_url or ''

class Announcement(models.Model):
    title=models.CharField(max_length=200)
    body=models.TextField()
    date_posted=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
    is_urgent=models.BooleanField(default=False)
    send_notification=models.BooleanField(default=False,help_text="Email subscribed members")
    class Meta: ordering=['-date_posted']
    def __str__(self): return self.title

class Testimony(models.Model):
    CATEGORY_CHOICES=[('Healing','Healing'),('Financial Breakthrough','Financial Breakthrough'),('Marriage & Family','Marriage & Family'),('Salvation','Salvation'),('Career & Education','Career & Education'),('Deliverance','Deliverance'),('General','General')]
    member=models.ForeignKey('MemberProfile',on_delete=models.SET_NULL,null=True,blank=True,related_name='testimonies')
    name=models.CharField(max_length=100,verbose_name="Full Name")
    location=models.CharField(max_length=150,blank=True,default="Worldwide")
    testimony=models.TextField()
    category=models.CharField(max_length=50,choices=CATEGORY_CHOICES,default='General')
    photo_file=models.ImageField(upload_to='testimonies/',blank=True,null=True)
    photo_url=models.URLField(blank=True)
    date=models.DateField(auto_now_add=True)
    is_approved=models.BooleanField(default=False,help_text="Tick to show on website")
    is_featured=models.BooleanField(default=False)
    class Meta: ordering=['-is_featured','-date']; verbose_name_plural="Testimonies"
    def __str__(self): return f"Testimony by {self.name}"

class Flyer(models.Model):
    title=models.CharField(max_length=200)
    image_file=models.ImageField(upload_to='flyers/',blank=True,null=True,verbose_name="Flyer Image — Upload",help_text="Upload JPG/PNG/WEBP poster")
    image_url=models.URLField(blank=True,verbose_name="Flyer Image — URL",help_text="Or paste an online image URL")
    link_url=models.URLField(blank=True,help_text="Optional — clicking opens this URL")
    caption=models.CharField(max_length=300,blank=True)
    is_active=models.BooleanField(default=True)
    order=models.PositiveIntegerField(default=0)
    date_posted=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['order','-date_posted']; verbose_name="Church Flyer / Poster"; verbose_name_plural="Church Flyers / Posters"
    def __str__(self): return self.title
    def get_image(self):
        if self.image_file and self.image_file.name: return self.image_file.url
        return self.image_url or ''

class MemberProfile(models.Model):
    GENDER_CHOICES=[('M','Male'),('F','Female'),('other','Prefer not to say')]
    STATUS_CHOICES=[('new','New Member'),('regular','Regular Member'),('worker','Church Worker'),('minister','Minister')]
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    phone=models.CharField(max_length=20,blank=True)
    address=models.TextField(blank=True)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES,blank=True)
    membership_status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='new')
    photo_file=models.ImageField(upload_to='members/',blank=True,null=True)
    ministry_interest=models.CharField(max_length=200,blank=True)
    notify_events=models.BooleanField(default=True,verbose_name="Notify: New Events")
    notify_sermons=models.BooleanField(default=True,verbose_name="Notify: New Sermons")
    notify_announcements=models.BooleanField(default=True,verbose_name="Notify: Announcements")
    push_subscription=models.TextField(blank=True)
    date_registered=models.DateTimeField(auto_now_add=True)
    class Meta: verbose_name="Member Profile"; verbose_name_plural="Member Profiles"
    def __str__(self): return f"{self.user.get_full_name() or self.user.username}"

class NotificationLog(models.Model):
    TYPE_CHOICES=[('event','Event'),('announcement','Announcement'),('sermon','Sermon'),('general','General')]
    title=models.CharField(max_length=200)
    body=models.TextField()
    notif_type=models.CharField(max_length=20,choices=TYPE_CHOICES,default='general')
    sent_at=models.DateTimeField(auto_now_add=True)
    sent_count=models.PositiveIntegerField(default=0)
    class Meta: ordering=['-sent_at']
    def __str__(self): return f"[{self.notif_type}] {self.title}"
