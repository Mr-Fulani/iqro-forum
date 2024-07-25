from django.contrib import admin
from django.urls import path, include
from women import views
from women.views import page_not_found
from django.conf.urls.static import static
from . import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('women.urls')),
    path('users/', include('users.urls', namespace='users')),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # эту добавку только при отладке




handler404 = page_not_found


admin.site.site_header = 'Панель администрирования'
admin.site.index_title = 'Известные женщины мира'
