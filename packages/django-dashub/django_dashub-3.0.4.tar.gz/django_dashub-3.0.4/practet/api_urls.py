from django.urls import path, include

urlpatterns = [
    path('v1/', include('apps.subscription.urls')),
    path('v1/', include('apps.core.urls')),
    path('v1/', include('apps.user.urls')),
    path('v1/', include('apps.community.urls')),
    path('v1/', include('courses.ielts.urls')),
    path('v1/', include('apps.multitenant.urls')),
    path('v1/', include('apps.helpdesk.urls')),
]
