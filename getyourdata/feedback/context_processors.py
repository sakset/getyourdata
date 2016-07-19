from feedback.forms import NewFeedbackForm
from feedback.models import ServiceFeedback


def feedback_form(request):
    feedback_form = NewFeedbackForm()

    feedback_content = request.session.pop('feedback_content', False)
    if feedback_content:
        feedback_form = NewFeedbackForm(
            instance=ServiceFeedback(content=feedback_content))

    return {
        'feedback_form': feedback_form
    }
