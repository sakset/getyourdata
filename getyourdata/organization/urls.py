from django.conf.urls import url
from organization import views as organization_views

urlpatterns = [
    url(r'^view/(?P<org_id>\d+)/$', organization_views.view_organization, name="view_organization"),
    url(r'^new/$', organization_views.new_organization, name="new_organization"),
    url(r'^$', organization_views.list_organizations, name="list_organizations"),
]
