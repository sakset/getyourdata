from django import template

register = template.Library()


@register.simple_tag
def form_errors(*args, **kwargs):
    """
    Returns the form errors of a certain field, the field name and index
    counter to be passed as keyword arguments
    """

    form = kwargs["form"]
    field = kwargs["field"]
    counter = str(kwargs["counter"])

    # return either the errors or an empty string
    return form.errors.get("%s_%s" % (field, counter), "")


@register.simple_tag
def field_value(*args, **kwargs):
    """
    Return the value of a dynamic field

    Parameters are the same as in Form.form_errors() method
    """

    form = kwargs["form"]
    field = kwargs["field"]
    counter = str(kwargs["counter"])

    try:
        return form.data["%s_%s" % (field, counter)]
    except AttributeError:
        return ""
    except KeyError:
        return ""
