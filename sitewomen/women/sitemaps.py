from django.contrib.sitemaps import Sitemap

from women.models import Women, Category

from django.contrib.sitemaps import GenericSitemap
from .models import Women, Category



posts_info_dict = {
    "queryset": Women.published.all(),
    "date_field": "time_update",
}

cats_info_dict = {
    "queryset": Category.objects.all(),
}

sitemaps = {
    "posts": GenericSitemap(posts_info_dict, priority=0.7, changefreq='weekly'),
    "cats": GenericSitemap(cats_info_dict, priority=0.5, changefreq='weekly'),
}


