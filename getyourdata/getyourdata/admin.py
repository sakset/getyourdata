from django.contrib import admin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django.utils.translation import ugettext_lazy as _

from modeltranslation.admin import TranslationAdmin
from tinymce.widgets import AdminTinyMCE


admin.site.unregister(FlatPage)


@admin.register(FlatPage)
class FlatPageAdmin(TranslationAdmin):
    form = FlatpageForm
    fieldsets = (
        (None,
        {'fields': (
            'url',
            'title',
            'content',
            'sites',
            )}
        ),
    )
    list_display = ('url', 'title')
    formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE},
    }
