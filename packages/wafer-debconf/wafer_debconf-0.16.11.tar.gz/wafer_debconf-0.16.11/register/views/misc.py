from django.conf import settings

from bursary.models import Bursary
from register.forms.misc import MiscForm
from register.models.attendee import Attendee
from register.views.core import RegisterStep


class MiscView(RegisterStep):
    title = 'Anything Else?'
    form_class = MiscForm

    def get_initial(self):
        user = self.request.user
        initial = {
            'notes': self.request.user.attendee.notes
        }
        try:
            bursary = user.bursary
        except Bursary.DoesNotExist:
            pass
        else:
            for field in bursary._meta.get_fields():
                if field.is_relation:
                    continue
                initial[field.name] = getattr(bursary, field.name)
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['contributions'] = self.request_contributions()
        return kwargs

    def request_contributions(self):
        user = self.request.user
        try:
            bursary = user.bursary
        except Bursary.DoesNotExist:
            bursary = Bursary()
        return (
            settings.DEBCONF_REVIEW_FREE_ATTENDEES
            and not user.attendee.billable()
            and not bursary.potential_bursary())

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data
        bursary_data = data.copy()
        attendee_data = {'notes': bursary_data.pop('notes')}
        bursary_data.update({
            'request_food': False,
            'request_accommodation': False,
            'request_travel': False,
            'request_expenses': False,
        })

        user.attendee  # We should never be creating, here
        user.attendee = Attendee.objects.update_or_create(
            user=user, defaults=attendee_data)[0]

        if self.request_contributions():
            user.bursary = Bursary.objects.update_or_create(
                user=user, defaults=bursary_data)[0]

        return super().form_valid(form)
