from django.shortcuts import render

from home.models import HomePage

def home(request):
    page, created = HomePage.objects.get_or_create(admin_name='home')
    return render(request, 'home/home.html', {
        'content': page.content,
    })
