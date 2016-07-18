from django.shortcuts import render
from django.core.cache import cache

from home.models import HomePage


def home(request):
    """
    Simply displays the front page
    """
    page = cache.get("home_page")

    if page is None:
        page, created = HomePage.objects.get_or_create(admin_name='default')
        cache.set("home_page", page, 60)

    return render(request, 'home/home.html', {
        'content': page.content,
    })
