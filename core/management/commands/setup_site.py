from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ChurchSettings, ServiceTime


class Command(BaseCommand):
    help = 'Set up initial site data'

    def handle(self, *args, **kwargs):
        # Create admin if not exists
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@church.com', 'Admin1234!')
            self.stdout.write(self.style.SUCCESS('Admin user created'))

        # Ensure settings record exists
        s = ChurchSettings.get_settings()
        self.stdout.write(self.style.SUCCESS(f'Settings OK: {s.church_name}'))

        # Seed default service times if none exist
        if not ServiceTime.objects.exists():
            ServiceTime.objects.create(day='sunday', service_name='1st Service', start_time='07:30', order=1)
            ServiceTime.objects.create(day='sunday', service_name='2nd Service', start_time='09:30', order=2)
            ServiceTime.objects.create(day='wednesday', service_name='Bible Study', start_time='18:00', order=3)
            self.stdout.write(self.style.SUCCESS('Default service times created'))

        self.stdout.write(self.style.SUCCESS('Site setup complete'))
