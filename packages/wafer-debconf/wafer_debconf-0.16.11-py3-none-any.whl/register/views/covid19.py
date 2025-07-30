from register.forms.covid19 import Covid19Form
from register.views.core import RegisterStep
from register.models.attendee import Attendee


class Covid19View(RegisterStep):
    title = 'COVID-19'
    form_class = Covid19Form
    template_name = 'register/page/covid19.html'

    def get_initial(self):
        attendee = self.request.user.attendee
        initial = {
            'vaccinated': attendee.vaccinated,
            'vaccination_notes': attendee.vaccination_notes,
            'confirm_covid_tests': attendee.confirm_covid_tests,
        }
        return initial

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data

        user.attendee  # We should never be creating, here
        user.attendee = Attendee.objects.update_or_create(
            user=user, defaults=data)[0]

        return super().form_valid(form)
