from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

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