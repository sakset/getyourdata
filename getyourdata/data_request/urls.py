from django.conf.urls import url

from data_request import views as data_request_views


urlpatterns = [
    url(r'^new/(?P<organization_id>\d+)$', data_request_views.request_data, name='request_data'),
]