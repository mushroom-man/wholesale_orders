from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Markwood Mushrooms"
admin.site.site_title = "Markwood Mushrooms Admin"
admin.site.index_title = "Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
