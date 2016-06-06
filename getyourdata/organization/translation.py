from modeltranslation.translator import register, TranslationOptions
from organization.models import AuthenticationField


@register(AuthenticationField)
class AuthenticationFieldTranslationOptions(TranslationOptions):
    fields = ('title',)

