from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin

from filebrowser.sites import site as filebrowser_site
from grappelli import urls as grappelli_urls
from tinymce import urls as tinymce_urls


from home import views as home_views


urlpatterns = i18n_patterns(
    url(r'^$', home_views.home, name="home"),
    url(r'^organizations/', include(
        'organization.urls', namespace="organization")),
    url(r'^request/', include('data_request.urls', namespace="data_request")),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls', namespace="api")),
    url(r'^request/', include(
        'data_request.urls', namespace="data_request")),
    url(r'^admin/filebrowser/', include(filebrowser_site.urls)),
    url(r'^grappelli/', include(grappelli_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include(tinymce_urls)),
)

urlpatterns += [url(r'^i18n/', include('django.conf.urls.i18n'))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += url(r'^rosetta/', include('rosetta.urls')),
