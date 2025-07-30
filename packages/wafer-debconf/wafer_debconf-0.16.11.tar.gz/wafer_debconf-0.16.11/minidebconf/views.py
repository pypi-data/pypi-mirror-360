from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse
from minidebconf.forms import register_form_factory
from minidebconf.models import Registration, is_registered


class RegistrationMixin:
    @property
    def user(self):
        return self.request.user

    def get_object(self):
        if is_registered(self.user):
            return Registration.objects.get(user=self.user)
        else:
            return Registration(user=self.user)



class RegisterView(LoginRequiredMixin, RegistrationMixin, UpdateView):
    template_name = 'minidebconf/register.html'

    def dispatch(self, request, *args, **kwargs):
        if not settings.WAFER_REGISTRATION_OPEN:
            raise PermissionDenied("Registration is closed")
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return register_form_factory()

    def get_success_url(self):
        return reverse('registration_finished')


class UnregisterView(LoginRequiredMixin, RegistrationMixin, DeleteView):

    def get_success_url(self):
        return reverse('wafer_user_profile', args=[self.user.username])


class RegistrationFinishedView(LoginRequiredMixin, TemplateView):
    template_name = 'minidebconf/registration_finished.html'
