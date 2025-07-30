from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from minidebconf.models import Diet, Registration, RegistrationType, ShirtSize


class RegistrationAdmin(admin.ModelAdmin):
    readonly_fields = ["name", "email"]

    @admin.display(description=_("Full name"))
    def name(self, registration):
        return registration.user.get_full_name()

    @admin.display(description=_("Email"))
    def email(self, registration):
        return registration.user.email

    @admin.display(description=_("Involvement"))
    def _involvement(self, registration):
        return registration.get_involvement_display()

    @admin.display(boolean=True, description=_("Accomodation"))
    def accommodation(self, registration):
        return registration.arranged_accommodation

    @admin.display(boolean=True, description=_("Food"))
    def food(self, registration):
        return registration.arranged_food

    @admin.display(boolean=True, description=_("Travel"))
    def travel(self, registration):
        return registration.travel_reimbursement

    def get_fields(self, request, obj=None):
        return ["name", "email"] + super().get_fields(request, obj)

    def get_list_display(self, request):
        __list_display__ = (
            "name",
            "email",
            "phone_number" if settings.MINIDEBCONF_REGISTER_PHONE else None,
            "registration_type" if RegistrationType.objects.count() > 1 else None,
            "_involvement",
            "gender",
            "country",
            "city_state",
            "diet" if Diet.objects.count() > 1 else None,
            "shirt_size" if ShirtSize.objects.count() > 1 else None,
            "accommodation",
            "food",
            "travel",
            "travel_cost",
        )
        return [f for f in __list_display__ if f]

    list_filter = (
        "registration_type",
        "involvement",
        "gender",
        "days",
        "diet",
        "shirt_size",
        "arranged_accommodation",
        "arranged_food",
        "travel_reimbursement",
    )


admin.site.register(Registration, RegistrationAdmin)
admin.site.register(RegistrationType)
admin.site.register(Diet)
admin.site.register(ShirtSize)
