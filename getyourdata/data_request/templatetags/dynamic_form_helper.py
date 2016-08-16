from django import template

register = template.Library()

@register.simple_tag
def form_errors(*args, **kwargs):
    """
    Returns the form errors of a certain field, the field name and index counter to be
    passed as keyword arguments
    """

    form=kwargs["form"]
    field=kwargs["field"]
    counter=str(kwargs["counter"])

    # return either the errors or an empty string
    return form.errors.get(field + "_" + counter, "")


@register.simple_tag
def field_value(*args, **kwargs):
    """
    return the value of a dynamic field, parameters the same as form_errors method
    """

    form=kwargs["form"]
    field=kwargs["field"]
    counter=str(kwargs["counter"])

    try:
        return form.data[field + "_" + counter]
    except AttributeError:
        return ""
    except KeyError:
        return ""
