from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views as flatpage_views

from filebrowser.sites import site as filebrowser_site
from grappelli import urls as grappelli_urls
from tinymce import urls as tinymce_urls

from home import views as home_views
from data_request import views as data_request_views


urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^admin/filebrowser/', include(filebrowser_site.urls)),
    url(r'^grappelli/', include(grappelli_urls)),
    url(r'^tinymce/', include(tinymce_urls)),

    url(r'^api/', include('api.urls', namespace="api")),

    url(r'^$', home_views.home, name="home"),
    url(r'^organizations/', include(
        'organization.urls', namespace="organization")),
    url(r'^request/', include('data_request.urls', namespace="data_request")),
    url(r'^feedback/', include('feedback.urls', namespace="feedback")),
    url(r'^request/', include(
        'data_request.urls', namespace="data_request")),
    url(r'^faq/', data_request_views.faq, name='faq'),
    url(r'^(?P<url>.*/)$', flatpage_views.flatpage),

)

urlpatterns += [
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += url(r'^rosetta/', include('rosetta.urls')),
