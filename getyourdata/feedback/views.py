from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from feedback.forms import NewFeedbackForm


def send_feedback(request):
    if request.method == "POST":
        form = NewFeedbackForm(request.POST)
        form_valid = form.is_valid()

        if form_valid:
            feedback = form.save()
            messages.success(request, _('Thank you for your feedback!'))
        else:
            request.session['feedback_content'] = request.POST.get('content')

            for error in form['content'].errors:
                messages.error(request, "%s: %s" % (
                    form['content'].label, error))

    return redirect(reverse('home'))
