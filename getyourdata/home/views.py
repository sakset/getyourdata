from django.http import HttpResponse
from django.template import Template, RequestContext

from home.models import HomePage


def home(request):
    """
    Displays the default front page
    """
    page, created = HomePage.objects.get_or_create(admin_name='default')
    return HttpResponse(Template(page.content).render(RequestContext(request, {
            "my_name": "Adrian",
        })
    ))
