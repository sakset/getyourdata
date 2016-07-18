from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

#from getyourdata.forms import CaptchaForm
from feedback.forms import NewFeedbackForm

def send_feedback(request): #captcha
    if request.method == "POST":
        #captcha_form = CaptchaForm(request.POST)
        form = NewFeedbackForm(request.POST)
        #captcha_valid = captcha_form.is_valid()
        form_valid = form.is_valid()
        
        if form_valid: #and captcha_valid:
            feedback = form.save()
            messages.success(request, _('Thank you for your feedback!'))
        else:
            print("*****************************************************************")
            print(form['content'].value)
            request.session['feedback_content'] = request.POST.get('content')

            for error in form['content'].errors:
                messages.error(request, form['content'].label+": "+error)
        #    if not captcha_valid:
        #        messages.error(request, _("You're a robot.. Please accept captcha!"))
    return redirect(reverse('home'))

        
