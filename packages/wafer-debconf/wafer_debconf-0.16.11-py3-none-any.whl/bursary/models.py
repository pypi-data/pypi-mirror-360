from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site

from debconf.tz import aoe_datetime
from invoices.models import Invoice


BURSARY_STATUS_CHOICES = (
    ('submitted', 'The bursary request has been submitted'),
    ('ranked', 'The bursary request has been ranked'),
    ('pending', 'The bursary request has been granted '
                'and is pending your acceptance'),
    ('accepted', 'The attendee has accepted the bursary grant'),
    ('denied', 'The bursary request has been denied'),
    ('expired', 'The bursary grant has expired'),
    ('canceled', 'The bursary request has been canceled'),
)

CONTRIB_RANKING_HELP_TEXT = """

Decimal value from 0 to 5; Please try to conform to the following scale for
your assessment.

<dl>
<dt>5 "Must fund"</dt>
<dd>
If this person does not attend DebConf, there will be significant
negative impact for DebConf or Debian more generally.
</dd>
<dt>4 "Priority funding"</dt>
<dd>
There are clear benefits to Debian or to DebConf of this person attending
debconf. This might be an accepted talk that seems particularly important.
</dd>
<dt>3 "Good initiative"</dt>
<dd>
We should fund this person because they propose something interesting.
</dd>
<dt>2 "Good record"</dt>
<dd>
This person has a record of substantial contribution to Debian.this should
generally be recent contribution, i.e. within the last two years.
</dd>
<dt>1 "OK"</dt>
<dd>
If we have budget, I don't object to funding this request.
</dd>
<dt>0 "Deny"</dt>
<dd>
Even if we have budget, I think we should not fund this request.
</dd>
</dl>
"""

OUTREACH_RANKING_HELP_TEXT = """

Decimal value from 0 to 5; Please try to assess applicants according to the
following criteria, and to use the full scale across your (non-null) ratings.

<ul>
<li>Gender (favoring women (cis, trans, queer), non-binary and genderqueer
individuals, as well as trans men)</li>
<li>Age (favoring individuals over 35 years old)</li>
<li>Country of origin / ethnic diversity</li>
<li>Whether the applicant is a newcomer to Debian (yes should rank higher)</li>
</ul>

"""


def budget_choices(user = None):
    """Generate the options for budget."""
    for key, options in settings.DEBCONF_BURSARY_BUDGETS.items():
        if user and not user.has_perms(options.get('permissions', [])):
            continue
        yield (key, options['description'])


class Bursary(models.Model):
    BURSARY_NEEDS = OrderedDict((
        ('unable', 'Without this funding, I will be absolutely '
                   'unable to attend'),
        ('sacrifice', 'Without the requested funding, I will have to '
                      'make financial sacrifices to attend'),
        ('inconvenient', 'Without the requested funding, attending will '
                         'be inconvenient for me'),
        ('non-financial', 'I am not applying based on financial need'),
    ))
    CAN_UPDATE_STATUSES = ('submitted', 'ranked', 'pending')
    # Linked to User rather than Attendee, so we don't lose track if someone
    # unregisters
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='bursary',
                                on_delete=models.PROTECT)

    budget = models.CharField(max_length=16, choices=list(budget_choices()))

    # Request:
    request_food = models.BooleanField()
    request_accommodation = models.BooleanField()
    request_travel = models.BooleanField()
    request_expenses = models.BooleanField()

    reason_contribution = models.TextField(blank=True)
    reason_plans = models.TextField(blank=True)
    reason_diversity = models.TextField(blank=True)
    need = models.CharField(max_length=16,
                            choices=BURSARY_NEEDS.items(), blank=True)
    travel_bursary = models.IntegerField(null=True, blank=True)
    travel_from = models.TextField(blank=True)

    partial_contribution = models.IntegerField(null=True, blank=True)

    # Review:
    food_status = models.CharField(max_length=32,
                                   choices=BURSARY_STATUS_CHOICES,
                                   default='submitted')
    food_accept_before = models.DateField(null=True, blank=True)

    accommodation_status = models.CharField(max_length=32,
                                            choices=BURSARY_STATUS_CHOICES,
                                            default='submitted')
    accommodation_accept_before = models.DateField(null=True, blank=True)

    travel_status = models.CharField(max_length=32,
                                     choices=BURSARY_STATUS_CHOICES,
                                     default='submitted')
    travel_accept_before = models.DateField(null=True, blank=True)

    reimbursed_amount = models.IntegerField(default=0, blank=True)

    expenses_status = models.CharField(max_length=32,
                                       choices=BURSARY_STATUS_CHOICES,
                                       default='submitted')
    attendance_status = models.CharField(max_length=32,
                                         choices=BURSARY_STATUS_CHOICES,
                                         default='submitted')
    class Meta:
        verbose_name = 'bursary request'
        permissions = (
            ("review_attendance", "Can review attendance requests"),
        )

    @property
    def request_any(self):
        return (self.request_food or self.request_accommodation
                or self.request_travel or self.request_expenses)

    def potential_bursary(self, key=None):
        potential_bursary_status = frozenset((
            'submitted', 'ranked', 'pending', 'accepted'))
        if now() > aoe_datetime(settings.DEBCONF_BURSARY_ACCEPTANCE_DEADLINE):
            potential_bursary_status = frozenset(('accepted',))
        return self.status_in(key, potential_bursary_status)

    def can_update(self, key=None):
        ret = False
        if key is None or key == 'travel':
            ret = self.request_travel and self.travel_status == 'accepted'
        return ret or self.status_in(
            key=key, statuses=self.CAN_UPDATE_STATUSES
        )

    def status_in(self, key, statuses):
        """Return boolean result for whether a bursary for key has been
        requested and is in one of the listed statuses.
        If key is None, check all possible types of bursary.
        """

        if key == 'food':
            return (self.request_food
                    and self.food_status in statuses)
        elif key == 'accommodation':
            return (self.request_accommodation
                    and self.accommodation_status in statuses)
        elif key == 'travel':
            return (self.request_travel
                    and self.travel_status in statuses)
        elif key is None:
            return (self.status_in('food', statuses)
                    or self.status_in('travel', statuses)
                    or self.status_in('accommodation', statuses))
        else:
            raise ValueError('Unknown key for status_in %s' % key)

    def must_accept(self):
        return 'pending' in (self.food_status, self.accommodation_status,
                             self.travel_status)

    def notify_status(self, request):
        if not self.request_any:
            if self.attendance_status != 'submitted':
                self.notify_attendance(request)
            return

        from_email = 'bursaries@debconf.org'
        to = self.user.email
        subject = ("Your bursary request for %s: status updated" %
                   get_current_site(request).name)
        body = render_to_string(
            'bursary/notify_status.txt', {
                'object': self,
                'profile_url': request.build_absolute_uri(
                    reverse('wafer_user_profile', args=(self.user.username,))
                ),
            }, request=request)

        msg = EmailMultiAlternatives(subject, body, to=[to],
                                     from_email=from_email)

        msg.send()

    def notify_attendance(self, request):
        from_email = 'registration@debconf.org'
        to = self.user.email
        subject = ("Your registration request for %s: status updated" %
                   get_current_site(request).name)
        body = render_to_string(
            'bursary/notify_attendance_status.txt', {
                'object': self,
            }, request=request)

        msg = EmailMultiAlternatives(subject, body, to=[to],
                                     from_email=from_email)

        msg.send()

    def __str__(self):
        return 'Bursary <{}>'.format(self.user.username)

    def budget_description(self):
        return settings.DEBCONF_BURSARY_BUDGETS[self.budget]['description']


def validate_score(score):
    if not 0 <= score <= 5:
        raise ValidationError(
            _('%(score)s should be between 0 and 5 inclusive'),
            params={'score': score}
        )


def check_bursaryreferee_permission():
    # XXX olasd: this returns duplicates,
    #            and limit_choices_to can't do better :(

    content_type = ContentType.objects.get_for_model(BursaryReferee)
    permission = Permission.objects.get(codename='change_bursaryreferee',
                                        content_type=content_type)
    return (Q(groups__permissions=permission)
            | Q(user_permissions=permission))


class BursaryReferee(models.Model):
    bursary = models.ForeignKey(Bursary, related_name='referees',
                                on_delete=models.CASCADE)
    referee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to=check_bursaryreferee_permission,
    )

    contrib_score = models.DecimalField(
        null=True, verbose_name="Contribution score",
        help_text=CONTRIB_RANKING_HELP_TEXT,
        decimal_places=2,
        max_digits=3,
        validators=[validate_score],
        blank=True,
    )

    outreach_score = models.DecimalField(
        null=True, verbose_name="Diversity and Inclusion score",
        help_text=OUTREACH_RANKING_HELP_TEXT,
        decimal_places=2,
        max_digits=3,
        validators=[validate_score],
        blank=True,
    )

    notes = models.TextField(
        default='', verbose_name="Notes for evaluation",
        help_text="Let us know how you came to your decision",
        blank=True,
    )

    final = models.BooleanField(
        default=False, verbose_name="Final assessment",
    )

    class Meta:
        permissions = [
            ("invited_speaker", "May have travel funded as a speaker"),
            ("orga_travel", "May have travel funded as an event organizer"),
        ]
        unique_together = ('bursary', 'referee')


    def __str__(self):
        referee_username = '???'
        if self.referee:
            referee_username = self.referee.username
        return 'BursaryReferee <{} ({}){}>'.format(
            self.bursary.user.username,
            referee_username,
            ' final' if self.final else '',
        )


@receiver(pre_save, sender=Bursary)
def auto_approve_attendance_on_bursary_acceptance(sender, instance, **kwargs):
    if instance.status_in(None, 'accepted'):
        instance.attendance_status = 'accepted'


@receiver(post_save, sender=Invoice)
def auto_approve_attendance_on_payment(sender, instance, **kwargs):
    try:
        recipient = instance.recipient
        bursary = recipient.bursary
        attendee = recipient.attendee
    except ObjectDoesNotExist:
        return
    if instance.status == 'paid' and attendee.paid():
        bursary.attendance_status = 'accepted'
        bursary.save()
