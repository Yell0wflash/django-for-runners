# coding: utf-8

from django.conf.urls import include, static, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path

# https://github.com/jedie/django-for-runners
from for_runners_project import settings

admin.autodiscover()

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    # until there is not real CMS pages: redirect to the interesting admin page:
    url(r"^$", RedirectView.as_view(url="/admin/for_runners/gpxmodel/")),
)

if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
