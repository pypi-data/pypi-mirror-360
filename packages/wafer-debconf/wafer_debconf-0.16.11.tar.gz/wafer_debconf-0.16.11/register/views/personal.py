from django.conf import settings

from register.forms.personal import PersonalInformationForm
from register.models.attendee import Attendee
from register.models.address import Address
from register.models.queue import Queue
from register.views.core import RegisterStep


class PersonalInformationView(RegisterStep):
    title = 'Personal Information'
    template_name = 'register/page/personal.html'
    form_class = PersonalInformationForm

    def get_initial(self):
        user = self.request.user
        initial = {}

        attendee = user.attendee
        for field in attendee._meta.get_fields():
            if field.is_relation:
                continue
            initial[field.name] = getattr(attendee, field.name)

        shipping_address = attendee.shipping_address
        if shipping_address:
            for field in shipping_address._meta.get_fields():
                if field.is_relation:
                    continue
                initial[f'shipping_{field.name}'] = getattr(
                    shipping_address, field.name)

        return initial

    def form_valid(self, form):
        user = self.request.user
        data = form.cleaned_data

        user.attendee  # We should never be creating, here
        user.attendee = Attendee.objects.update_or_create(
            user=user, defaults=data)[0]

        if form.cleaned_data['t_shirt_size'] or form.cleaned_data['shoe_size']:
            if settings.DEBCONF_ONLINE:
                Address.objects.update_or_create(
                    attendee=user.attendee, role='shipping',
                    defaults={
                        field[9:]: value
                        for field, value in data.items()
                        if field.startswith('shipping_')
                    })
        else:
            Address.objects.filter(
                attendee=user.attendee, role='shipping').delete()

        return super().form_valid(form)

    def registration_completed(self, attendee):
        if attendee.t_shirt_size or attendee.shoe_size:
            queue = Queue.objects.get_or_create(name='Swag')[0]
            queue.slots.get_or_create(attendee=attendee)
        if attendee.pgp_fingerprints and settings.ISSUE_KSP_ID:
            queue = Queue.objects.get_or_create(name='PGP Keysigning')[0]
            queue.slots.get_or_create(attendee=attendee)
