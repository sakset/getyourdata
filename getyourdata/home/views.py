from django.shortcuts import render
from django.core.cache import cache

from home.models import HomePage


def home(request):
    """
    Simply displays the front page
    """
    page, created = HomePage.objects.get_or_create(admin_name='default')
    return render(request, 'home/home.html', {
        'content': page.content,
    })
