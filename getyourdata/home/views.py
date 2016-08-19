from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from home.models import HomePage, FaqContent


def home(request):
    """
    Simply displays the front page
    """
    page = cache.get("home_page")

    if page is None:
        try:
            page = HomePage.objects.get(admin_name='default')
        except ObjectDoesNotExist:
            page = HomePage.objects.create_default()

        cache.set("home_page", page)

    return render(request, 'home/home.html', {
        'content': page.content,
    })


def faq(request):
    """
    Show the FAQ page
    """
    faqs = cache.get("faqs")

    if faqs is None:
        faqs = FaqContent.objects.order_by("priority")
        cache.set("faqs", faqs)
        
    return render(request, 'home/faq/faq.html', {"faqs": faqs})
