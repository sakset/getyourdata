from django.conf.urls import url

from feedback import views as feedback_views


urlpatterns = [
    url(r'^send/$',
        feedback_views.send_feedback, name='send_feedback'),
    url(r'^send_json/$',
        feedback_views.send_feedback_json, name='send_feedback_json'),
]
