from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def get_urls(self, page=1, site=None, protocol=None):
        site = Site(domain='www.glafa.org', name='GLAFA')
        return super(StaticViewSitemap, self).get_urls(page=page, site=site, protocol=protocol)

    def items(self):
        return [
            'home',
            'sermons',
            'events',
            'about',
            'give',
            'contact',
            'new_visitor',
            'testimonies',
            'live',
        ]

    def location(self, item):
        return reverse(item)