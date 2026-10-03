from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

# 1x1 transparent PNG
PNG = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00'
       b'\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7\x9a\xa0\xa0'
       b'\x00\x00\x00\x00IEND\xaeB`\x82')


class Command(BaseCommand):
    help = 'Test that image uploads really reach Cloudinary (uploads then deletes a 1px test image).'

    def handle(self, *args, **kwargs):
        self.stdout.write(f'Storage in use : {default_storage.__class__.__module__}.{default_storage.__class__.__name__}')
        self.stdout.write(f'Cloud name     : {getattr(settings, "CLOUDINARY_CLOUD_NAME", "") or "(missing)"}')
        self.stdout.write(f'API key        : {"set" if getattr(settings, "CLOUDINARY_API_KEY", "") else "(missing)"}')
        self.stdout.write(f'API secret     : {"set" if getattr(settings, "CLOUDINARY_API_SECRET", "") else "(missing)"}')

        if not getattr(settings, 'USING_CLOUDINARY', False):
            self.stdout.write(self.style.ERROR(
                'FAIL: Cloudinary credentials not found. Uploads are going to local disk. '
                'Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET.'))
            return
        try:
            name = default_storage.save('diagnostics/ping.png', ContentFile(PNG))
            url = default_storage.url(name)
            self.stdout.write(self.style.SUCCESS(f'OK: uploaded to Cloudinary -> {url}'))
            default_storage.delete(name)
            self.stdout.write('Test image deleted.')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'FAIL: Cloudinary rejected the upload: {type(e).__name__}: {e}'))
            self.stdout.write('Usual causes: wrong cloud name, wrong API key/secret, extra spaces or quotes in a value.')
