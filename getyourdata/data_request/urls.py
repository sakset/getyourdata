from django.conf.urls import url

from data_request import views as data_request_views


urlpatterns = [
    url(r'^new/(?P<org_ids>[\w,]+)$', data_request_views.request_data,
        name='request_data'),
    # List of organization IDs can also be passed as a POST parameter
    url(r'^new/$', data_request_views.request_data, name='request_data'),
    url(
        r'^feedback/(?P<org_ids>[\w,]+)$',
        data_request_views.give_feedback, name="give_feedback"),
    # feedback submit, org_ids passed as POST variable
    url(r'^feedback/$',
        data_request_views.submit_feedback, name="submit_feedback"),
]
