from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def get_urls(self, page=1, site=None, protocol=None):
        class MockSite():
            domain = 'www.glafa.org'
            name = 'GLAFA'

        return super(StaticViewSitemap, self).get_urls(
            page=page,
            site=MockSite(),
            protocol='https'
        )


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
