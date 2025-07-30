import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from invoices.models import Invoice, InvoiceLine
from register.dates import get_ranges_for_dates

DEBCONF_NAME = settings.DEBCONF_NAME
INVOICE_PREFIX = settings.INVOICE_PREFIX
PRICES = settings.PRICES


def meal_prices():
    """Return a dict of meal name: price
    And the currency the prices are specified in.
    """
    prices = {name: meal['price']
              for name, meal in settings.PRICES['meal'].items()}
    prices['currency'] = settings.DEBCONF_BILLING_CURRENCY
    return prices


def meal_price_string():
    """Return a human-readable string of daily meal prices"""
    prices = meal_prices()
    s = [f'{meal.title()} {prices[meal]} {settings.DEBCONF_BILLING_CURRENCY}'
         for meal in ('breakfast', 'lunch', 'brunch', 'dinner')
         if meal in prices]
    return ', '.join(s) + '.'


def invoice_user(user, force=False, save=False):
    from bursary.models import Bursary

    attendee = user.attendee

    try:
        bursary = user.bursary
    except Bursary.DoesNotExist:
        bursary = Bursary()

    lines = []
    fee = PRICES['fee'][attendee.fee]
    if fee['price']:
        lines.append(InvoiceLine(
            reference='{}REG-{}'.format(INVOICE_PREFIX, attendee.fee.upper()),
            description='{} {} registration fee'.format(
                DEBCONF_NAME, fee['name']),
            unit_price=fee['price'],
            quantity=1,
        ))

    try:
        accomm = attendee.accomm
    except ObjectDoesNotExist:
        accomm = None

    if accomm and not bursary.potential_bursary('accommodation'):
        for line in invoice_accomm(accomm):
            lines.append(InvoiceLine(**line))

    try:
        food = attendee.food
    except ObjectDoesNotExist:
        food = None

    if food and not bursary.potential_bursary('food'):
        for line in invoice_food(food, accomm):
            lines.append(InvoiceLine(**line))

    for line in invoice_daytrip(attendee):
        lines.append(InvoiceLine(**line))

    if bursary.partial_contribution and (
            bursary.potential_bursary('accommodation') or
            bursary.potential_bursary('food')):
        lines.append(InvoiceLine(
            reference='CONTRIB',
            description='Partial bursary contribution',
            unit_price=bursary.partial_contribution,
            quantity=1,
        ))

    for paid_invoice in user.invoices.filter(status='paid', compound=False):
        lines.append(InvoiceLine(
            reference='INV#{}'.format(paid_invoice.reference_number),
            description='Previous Payment Received',
            unit_price=-paid_invoice.total,
            quantity=1,
        ))

    invoice = Invoice(
        recipient=user,
        status='new',
        date=timezone.now(),
        invoiced_entity=attendee.invoiced_entity,
        billing_address=attendee.billing_address
    )

    total = sum(line.total for line in lines)

    # Only save invoices if non-zero
    if save and total > 0:
        invoice.save()

    for i, line in enumerate(lines):
        line.line_order = i
        if save and total > 0:
            line.invoice_id = invoice.id
            line.save()

    return {
        'invoice': invoice,
        'lines': lines,
        'total': total,
        'total_local': total * settings.DEBCONF_LOCAL_CURRENCY_RATE,
    }


def estimate_bursary_value(user, include_food=True, include_accommodation=True):
    """Estimate the value of user's bursary."""
    lines = []
    attendee = user.attendee
    bursary = user.bursary

    try:
        accomm = attendee.accomm
    except ObjectDoesNotExist:
        accomm = None

    if include_accommodation:
        if accomm and bursary.potential_bursary('accommodation'):
            for line in invoice_accomm(accomm, estimate_bursary_value=True):
                lines.append(InvoiceLine(**line))

    if include_food:
        try:
            food = attendee.food
        except ObjectDoesNotExist:
            food = None

        if food and bursary.potential_bursary('food'):
            for line in invoice_food(food, accomm):
                lines.append(InvoiceLine(**line))

    return sum(line.total for line in lines)


def invoice_food(food, accomm=None):
    """Generate one invoice line per meal type per consecutive stay"""
    from register.models.food import Meal

    accomm_included_meals = set()
    if accomm:
        accom_price = PRICES['accomm'][accomm.option]
        accomm_included_meals = accom_price.get('included_meals', set())

    for meal, meal_label in Meal.MEALS.items():
        dates = [entry.date for entry in food.meals.filter(meal=meal)
                 if not entry.conference_dinner]
        if not dates:
            continue
        if meal in accomm_included_meals:
            continue

        ranges = get_ranges_for_dates(dates)
        for first, last in ranges:
            n_meals = (last - first).days + 1

            if first != last:
                dates = '{} to {}'.format(first, last)
            else:
                dates = str(first)

            yield {
                'reference': '{}{}'.format(INVOICE_PREFIX, meal.upper()),
                'description': '{} {} ({})'.format(
                    DEBCONF_NAME, meal_label, dates),
                'unit_price': PRICES['meal'][meal]['price'],
                'quantity': n_meals,
            }

    if food.meals.filter(meal='dinner',
                         date=settings.DEBCONF_CONFERENCE_DINNER_DAY):
        food_price = PRICES['meal']['conference_dinner']
        yield {
            'reference': '{}CONFDINNER'.format(INVOICE_PREFIX),
            'description': '{} {} ({})'.format(
                DEBCONF_NAME,
                food_price.get('name', 'Conference Dinner'),
                settings.DEBCONF_CONFERENCE_DINNER_DAY.isoformat()),
            'unit_price': food_price['price'],
            'quantity': 1,
        }


def invoice_accomm(accomm, estimate_bursary_value=False):
    """Generate one invoice line per consecutive stay"""
    stays = get_ranges_for_dates(
        night.date for night in accomm.nights.all()
    )
    accom_price = PRICES['accomm'][accomm.option]

    if accom_price.get('paid_separately', False):
        return
    if 'price' in accom_price:
        unit_price = accom_price['price']
    else:
        if estimate_bursary_value:
            # Select the cheapest paid accommodation option
            unit_price = min(option['price']
                             for option in PRICES['accomm'].values()
                             if 'price' in option)
        else:
            return

    for first_night, last_night in stays:
        last_morning = last_night + datetime.timedelta(days=1)
        num_nights = (last_morning - first_night).days
        dates = "evening of %s to morning of %s" % (first_night,
                                                    last_morning)
        yield {
            'reference': f'{INVOICE_PREFIX}ACCOMM-{accomm.option.upper()}',
            'description':
                f'{DEBCONF_NAME} {accom_price["description"]} ({dates})',
            'unit_price': unit_price,
            'quantity': num_nights,
        }


def invoice_daytrip(attendee):
    """Generate one invoice line per day trip registration"""
    daytrip_option = attendee.daytrip_option
    if not daytrip_option:
        return
    daytrip = PRICES['daytrip'][daytrip_option]
    if not daytrip['price']:
        return

    yield {
        'reference': f'{INVOICE_PREFIX}DAYTRIP-{daytrip_option}',
        'description':
            f'{DEBCONF_NAME} Day Trip: {daytrip["description"]}',
        'unit_price': daytrip['price'],
        'quantity': 1,
    }

    try:
        attendee.travel_insurance
    except ObjectDoesNotExist:
        return

    if not daytrip['insurance_price']:
        return

    yield {
        'reference': f'{INVOICE_PREFIX}DAYTRIP-INSURANCE',
        'description':
            f'{DEBCONF_NAME} Day Trip Group Travel Insurance',
        'unit_price': daytrip['insurance_price'],
        'quantity': 1,
    }
