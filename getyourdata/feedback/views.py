from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from django.http import HttpResponse

from feedback.forms import NewFeedbackForm

import json


def send_feedback(request):
    """
    Send feedback and redirect to home
    """
    if request.method == "POST":
        form = NewFeedbackForm(request.POST)
        form_valid = form.is_valid()

        if form_valid:
            form.save()
            messages.success(request, _('Thank you for your feedback!'))
        else:
            request.session['feedback_content'] = request.POST.get('content')

            for error in form['content'].errors:
                messages.error(request, "%s: %s" % (
                    form['content'].label, error))

    return redirect(reverse('home'))


def send_feedback_json(request):
    """
    Send feedback and return a JSON reply
    """
    response = {"status": "error"}

    if request.method == "POST":
        form = NewFeedbackForm(request.POST)

        if form.is_valid():
            form.save()
            response["status"] = "success"
            response["message"] = _("Thank you for your feedback!")
        else:
            response["status"] = "error"
            response["message"] = ""

            for error, message in form.errors.iteritems():
                response["message"] += "%s" % message
    else:
        response["message"] = "This command requires HTTP POST to be used"

    return HttpResponse(json.dumps(response))
