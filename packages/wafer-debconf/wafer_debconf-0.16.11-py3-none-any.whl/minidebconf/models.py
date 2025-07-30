from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from django_countries.fields import CountryField

from wafer.schedule.models import ScheduleBlock
from debconf.countries import Countries
from debconf.models import GENDERS


INVOLVEMENT_LEVELS = (
    (0, _('Beginner')),
    (1, _('User')),
    (2, _('Contributor')),
    (4, _('Debian Maintainer (DM)')),
    (5, _('Debian Developer (DD)')),
)


class ShirtSize(models.Model):
    description = models.CharField(
        max_length=32,
        verbose_name=_("Description"))

    def __str__(self):
        return self.description


class Diet(models.Model):
    option = models.CharField(
        max_length=32,
        verbose_name=_("Diet"))

    def __str__(self):
        return self.option


class RegistrationType(models.Model):
    description = models.CharField(
        max_length=64,
        verbose_name=_("Description"),
    )

    def __str__(self):
        return self.description

class Registration(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('conference', 'registration')
        verbose_name_plural = pgettext_lazy('conference', 'registrations')

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(
        max_length=24,
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r"[^0-9() +-]", inverse_match=True)],
    )
    registration_type = models.ForeignKey(
        RegistrationType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    involvement = models.IntegerField(
        null=True,
        blank=True,
        choices=INVOLVEMENT_LEVELS,
        verbose_name=_("Level of involvement with Debian"),
    )
    gender = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=GENDERS.items(),
        verbose_name=_("Gender"),
    )
    country = CountryField(
        countries=Countries,
        null=True,
        blank=True,
        verbose_name=_("Country"),
    )
    city_state = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_("City/State or Province")
    )
    shirt_size = models.ForeignKey(
        ShirtSize,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Shirt size"),
    )

    arranged_accommodation = models.BooleanField(
        default=False,
        verbose_name=_("Conference-arranged accommodation"),
    )
    arranged_food = models.BooleanField(
        default=False,
        verbose_name=_("Conference-arranged food"),
    )
    diet = models.ForeignKey(
        Diet,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Diet"),
    )

    travel_reimbursement = models.BooleanField(
        default=False,
        verbose_name=_("Reimburse travel costs"),
    )
    travel_cost = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Travel costs"),
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes"),
    )

    # attendance info
    days =  models.ManyToManyField(
        ScheduleBlock,
        verbose_name=_('Which days you will attend'),
    )

    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        else:
            return None


def is_registered(user):
    return Registration.objects.filter(user=user).exists()
