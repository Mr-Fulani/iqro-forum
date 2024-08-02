
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from sitewomen import settings
from women import views
from women.views import page_not_found
from women.views import custom_permission_denied

from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_page
from women.sitemaps import sitemaps








handler403 = custom_permission_denied
handler404 = page_not_found




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('women.urls')),
    path('users/', include('users.urls', namespace="users")),
    path("__debug__/", include("debug_toolbar.urls")),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('captcha/', include('captcha.urls')),
    path('sitemap.xml', cache_page(86400)(sitemap), {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



admin.site.site_header = "Панель администрирования"
admin.site.index_title = "Известные женщины мира"
