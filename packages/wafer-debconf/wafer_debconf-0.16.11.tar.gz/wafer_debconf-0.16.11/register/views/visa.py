from register.forms.visa import VisaForm
from register.models.visa import Visa
from register.views.core import RegisterStep


class VisaView(RegisterStep):
    template_name = 'register/page/visa.html'
    title = 'Visa'
    form_class = VisaForm

    def get_initial(self):
        user = self.request.user
        initial = {
            'country': user.attendee.country,
        }

        try:
            visa = user.attendee.visa
        except Visa.DoesNotExist:
            return initial

        initial['country'] = visa.country
        initial['visa'] = bool(visa.country)

        return initial

    def form_valid(self, form):
        attendee = self.request.user.attendee
        data = form.cleaned_data.copy()

        if not data.pop('visa'):
            Visa.objects.filter(attendee=attendee).delete()
            return super().form_valid(form)

        visa = Visa.objects.update_or_create(
            attendee=attendee, defaults=data)[0]
        attendee.visa = visa

        return super().form_valid(form)
