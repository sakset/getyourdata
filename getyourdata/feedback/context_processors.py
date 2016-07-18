
from feedback.forms import NewFeedbackForm
#from getyourdata.forms import CaptchaForm
from feedback.models import ServiceFeedback

def feedback_form(request):
    feedback_form = NewFeedbackForm()
    #captcha_form = CaptchaForm()

    feedback_content = request.session.pop('feedback_content', False)
    if feedback_content:
        feedback_form = NewFeedbackForm(instance=ServiceFeedback(content=feedback_content))

    return {
        'feedback_form': feedback_form,
        #'captcha_form': captcha_form,
    }

