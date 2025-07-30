from django.conf import settings
from django.forms import Form

from register.views.core import RegisterStep
from register.models.accommodation import PAID_ACCOMMODATION


class InstructionsView(RegisterStep):
    template_name = "register/page/instructions.html"
    title = 'Instructions'
    form_class = Form  # Square peg in a round hole

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'DEBCONF_COLLECT_AFFILIATION': settings.DEBCONF_COLLECT_AFFILIATION,
            'DEBCONF_BURSARY_DEADLINE': settings.DEBCONF_BURSARY_DEADLINE,
            'DEBCONF_CONFIRMATION_DEADLINE':
                settings.DEBCONF_CONFIRMATION_DEADLINE,
            'DEBCONF_REVIEW_FREE_ATTENDEES':
                settings.DEBCONF_REVIEW_FREE_ATTENDEES,
            'PAID_ACCOMMODATION': PAID_ACCOMMODATION,
        })
        return context
