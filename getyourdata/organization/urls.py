from django.conf.urls import url
from organization import views as organization_views

urlpatterns = [
    url(r'$', organization_views.list_organizations, name="list_organizations"),
]
