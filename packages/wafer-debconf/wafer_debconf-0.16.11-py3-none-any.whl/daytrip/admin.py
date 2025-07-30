from django.contrib import admin

from daytrip.models import TravelInsurance


class TravelInsuranceAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'daytrip_option')
    search_fields = ('reference_number', 'attendee__user__username',
                     'attendee_user__first_name', 'attendee__user__last_name')

    def username(self, travel_insurance):
        return travel_insurance.attendee.user.username

    def full_name(self, travel_insurance):
        return travel_insurance.attendee.user.get_full_name()

    def daytrip_option(self, travel_insurance):
        return travel_insurance.attendee.daytrip_option


admin.site.register(TravelInsurance, TravelInsuranceAdmin)
