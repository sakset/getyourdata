from django.conf.urls import url
from organization import views as organization_views

urlpatterns = [
    url(r'new/$', organization_views.new_organization, name="new_organization"),
    url(r'$', organization_views.list_organizations, name="list_organizations"),
]
