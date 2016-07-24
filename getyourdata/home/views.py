from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from home.models import HomePage


def home(request):
    """
    Simply displays the front page
    """
    try:
        page = HomePage.objects.get(admin_name='default')
    except ObjectDoesNotExist:
        page = HomePage.objects.create_default()

    return render(request, 'home/home.html', {
        'content': page.content,
    })
