from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('filehub.urls')),
    path('', include('apps.dashboard.urls')),
    path('', admin.site.urls),
]
