from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("tracker.urls")),
    path("", include("users.urls")),
]

admin.site.site_header = "Finance Tracker Administration"

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
