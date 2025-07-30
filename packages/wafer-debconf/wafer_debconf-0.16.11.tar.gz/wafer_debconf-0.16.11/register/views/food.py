from register.dates import parse_date
from register.forms.food import FoodForm
from register.models.food import Food, Meal
from register.models.queue import Queue
from register.views.core import RegisterStep


class FoodView(RegisterStep):
    title = 'Food'
    template_name = 'register/page/food.html'
    form_class = FoodForm

    def get_initial(self):
        user = self.request.user
        initial = {}

        try:
            food = user.attendee.food
        except Food.DoesNotExist:
            return initial

        for field in food._meta.get_fields():
            if field.is_relation:
                continue
            initial[field.name] = getattr(food, field.name)

        initial['meals'] = [meal.form_name for meal in food.meals.all()
                            if not meal.conference_dinner]
        initial['conference_dinner'] = any(meal for meal in food.meals.all()
                                           if meal.conference_dinner)
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['attendee'] = self.request.user.attendee
        return kwargs

    def form_valid(self, form):
        attendee = self.request.user.attendee
        data = form.cleaned_data.copy()

        meals = data.pop('meals')

        if not meals:
            Food.objects.filter(attendee=attendee).delete()
            return super().form_valid(form)

        food = Food.objects.update_or_create(
            attendee=attendee, defaults=data)[0]
        attendee.food = food

        stored_meals = set(food.meals.all())
        requested_meals = set()
        for meal in meals:
            meal, date = meal.split('_')
            date = parse_date(date)
            requested_meals.add(Meal.objects.get(meal=meal, date=date))

        food.meals.remove(*(stored_meals - requested_meals))
        food.meals.add(*(requested_meals - stored_meals))

        return super().form_valid(form)

    def registration_completed(self, attendee):
        try:
            conference_dinner = any(meal for meal in attendee.food.meals.all()
                                    if meal.conference_dinner)
        except Food.DoesNotExist:
            conference_dinner = False
        if conference_dinner:
            queue = Queue.objects.get_or_create(name='Conference Dinner')[0]
            queue.slots.get_or_create(attendee=attendee)
