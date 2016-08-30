from django import template, forms
from django.utils.translation import get_language
from django.contrib.sites.models import Site

register = template.Library()


@register.filter(name='change_url_lang')
def change_url_lang(value, new_language):
    current_language = get_language()

    return value.replace("%s/" % current_language, "%s/" % new_language)


@register.filter(name='hide_form')
def hide_form(form):
    """
    Hide all of the form's fields
    """
    for name, field in form.fields.iteritems():
        form.fields[name].widget = forms.HiddenInput()

    return form

@register.simple_tag
def current_site():
    """
    Returns the current site object
    """
    return Site.objects.get_current().name