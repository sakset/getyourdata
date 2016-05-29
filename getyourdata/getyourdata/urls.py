from django.conf.urls import url, include
from django.contrib import admin

from home import views as home_views

urlpatterns = [
    url(r'^$', home_views.home, name="home"),
    url(r'^admin/', admin.site.urls),
    url(r'^organizations/', include(
        'organization.urls', namespace="organization")),
    url(r'^request/', include(
        'data_request.urls', namespace="data_request")),
]
