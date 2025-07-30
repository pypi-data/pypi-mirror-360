import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db.models import F, Q, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_duration
from django.utils.decorators import method_decorator
from django.views.generic import FormView, DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from bakery.views import BuildableTemplateView
from wafer.kv.models import KeyValue
from wafer.users.views import EditOneselfMixin

from volunteers.forms import (
    TasksFilterForm, VideoMassCreateTaskForm, VideoShirtForm,
    VolunteerUpdateForm)
from volunteers.models import Task, TaskTemplate, Volunteer


class TasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'wafer.volunteers/tasks.html'

    queryset = Task.objects.annotate_all().order_by('start', '-end',
                                                    'schedule_item',
                                                    'template__name', 'name')

    def get_context_data(self, **kwargs):
        context = super(TasksView, self).get_context_data(**kwargs)

        # TODO Find a better way
        if self.request.user.is_authenticated:
            volunteer, created = Volunteer.objects.get_or_create(
                user=self.request.user)

        if self.request.GET:
            filter_form = TasksFilterForm(self.request.GET,
                                          timezone=volunteer.timezone)
        else:
            filter_form = TasksFilterForm(timezone=volunteer.timezone)

        if filter_form.is_valid():
            filter_data = filter_form.cleaned_data
        else:
            filter_data = filter_form.initial

        context['filter_form'] = filter_form

        tasks = context['object_list'].filter(
            start__lte=filter_data['end'],
            end__gte=filter_data['start'],
        )

        if 'needed' in filter_data['extra_filters']:
            tasks = tasks.filter(
                nbr_volunteers__lt=F('max_volunteers'),
            )

        context['tasks'] = tasks

        if (self.request.user.is_authenticated and
                'preferred' in filter_data['extra_filters']):
            try:
                volunteer = Volunteer.objects.get(user=self.request.user)
                # TODO: add support for the preferred_tasks as well
                context['tasks'] = (
                    context['tasks'].filter(
                        Q(category__in=volunteer.preferred_categories.all())
                        | Q(template__in=volunteer.preferred_task_types.all())
                    )
                )
            except Volunteer.DoesNotExist:
                pass

        return context


class TaskView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'wafer.volunteers/task.html'

    queryset = Task.objects.annotate_all()

    def get_context_data(self, **kwargs):
        context = super(TaskView, self).get_context_data(**kwargs)
        # TODO Find a better way
        context['already_volunteer'] = (
            self.request.user.is_authenticated and
            self.object.volunteers.filter(user=self.request.user).exists()
        )
        context['can_volunteer'] = (
            self.request.user.is_authenticated and
            self.object.open_for_signup
        )

        context['concurrent_tasks'] = self.object.concurrent_tasks()

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        volunteer, new = Volunteer.objects.get_or_create(user=request.user)
        concurrently_volunteering = self.object.concurrent_tasks().filter(
            volunteers=volunteer).all()

        required_permission = self.object.get_required_permission()

        if self.object in volunteer.tasks.all():
            self.object.volunteers.remove(volunteer)
            messages.info(request, 'Removed')
        elif concurrently_volunteering:
            messages.error(request, (
                'You are already volunteering in this time-slot. {}. '
                'You can only be in one place at a time.'
            ).format(concurrently_volunteering[0]))
        elif self.object.nbr_volunteers >= self.object.max_volunteers:
            messages.error(request, 'This task already has enough volunteers.')
        elif not self.object.open_for_signup:
            messages.error(request,
                'This task has already ended. '
                'It is too late to volunteer for it.')
        elif required_permission and not request.user.has_perm(
                required_permission):
            messages.error(request,
                'Sorry, but this task requires volunteers to be trained first. '
                'Please talk to the the appropriate team, and they can train '
                'you. Thanks for helping out!')
        else:
            self.object.volunteers.add(volunteer)
            messages.success(request, 'Thank you for volunteering!')

        return redirect('wafer_task', pk=self.object.pk)


class VolunteerView(EditOneselfMixin, DetailView):
    model = Volunteer
    slug_field = 'user__username'
    template_name = 'wafer.volunteers/volunteer.html'

    def get_object(self, *args, **kwargs):
        # TODO Find a better way
        if self.request.user.is_authenticated:
            Volunteer.objects.get_or_create(user=self.request.user)

        return super(VolunteerView, self).get_object(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VolunteerView, self).get_context_data(**kwargs)
        context['profile'] = self.object.user.userprofile
        return context


class VolunteerUpdate(EditOneselfMixin, UpdateView):
    model = Volunteer
    slug_field = 'user__username'
    form_class = VolunteerUpdateForm
    template_name = 'wafer.volunteers/volunteer_update.html'

    def get_object(self, *args, **kwargs):
        # TODO Find a better way
        if self.request.user.is_authenticated:
            Volunteer.objects.get_or_create(user=self.request.user)

        return super(VolunteerUpdate, self).get_object(*args, **kwargs)

    def get_success_url(self):
        return reverse('wafer_volunteer',
                       kwargs={'slug': self.object.user.username})


class VideoMassScheduleView(LoginRequiredMixin, FormView):
    @method_decorator(permission_required('volunteers.add_task'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['lead_time'] = self.lead_time
        return kwargs

    @property
    def lead_time(self):
        lead_time = self.request.GET.get('lead_time')
        if lead_time:
            lead_time = parse_duration(lead_time)
        return lead_time or parse_duration('P1D')

    form_class = VideoMassCreateTaskForm
    template_name = 'wafer.volunteers/admin/video_mass_schedule.html'
    success_url = reverse_lazy('wafer_tasks')


class VideoShirtView(LoginRequiredMixin, FormView):
    form_class = VideoShirtForm
    template_name = 'wafer.volunteers/admin/video_shirts.html'
    success_url = reverse_lazy('wafer_tasks')

    @method_decorator(permission_required('volunteers.add_task'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        issued = []
        video_admin_group = Group.objects.get_by_natural_key('Volunteer Admin')
        for kv in KeyValue.objects.filter(
                group=video_admin_group, key='video_shirt',
                userprofile__isnull=False):
            userprofile = kv.userprofile_set.first()
            issued.append('{}: {}'.format(userprofile.user.username,
                                          userprofile.display_name()))
        context['issued'] = sorted(issued)

        return context


class VolunteerStatisticsView(BuildableTemplateView):
    build_path = 'volunteers/statistics/index.html'
    template_name = 'wafer.volunteers/statistics.html'
    cache_key = 'volunteers:statistics'
    cache_timeout = 30*60 if not settings.DEBUG else 10

    def get_context_data(self, **kwargs):
        retval = cache.get(self.cache_key)
        if retval:
            return retval

        volunteers_by_template = {}
        for template in TaskTemplate.objects.all():
            volunteers = Volunteer.objects.filter(tasks__template=template)
            volunteers_by_template[template.name] = {
                'unique_volunteers': volunteers.distinct().count(),
                'volunteers': volunteers.count(),
            }

        volunteers = []
        for volunteer in Volunteer.objects.all():
            if not volunteer.tasks.exists():
                continue
            total_task_data = (
                volunteer.tasks
                .annotate_all()
                .annotate(duration=F('end') - F('start'))
                .values('name_', 'duration')
                .annotate(total=Sum('duration'))
                .order_by('-total')
            )
            fav_task_data = total_task_data[0]
            total_duration = sum((type['total'] for type in total_task_data),
                                 datetime.timedelta())
            volunteers.append({
                'name': volunteer.user.userprofile.display_name(),
                'tasks': total_duration,
                'favourite_task': fav_task_data['name_'],
                'favourite_task_count': fav_task_data['total'],
            })

        volunteers.sort(key=lambda v: v['tasks'], reverse=True)

        retval = {
            'volunteers': volunteers,
            'volunteers_by_template': volunteers_by_template,
        }

        cache.set(self.cache_key, retval, self.cache_timeout)
        return retval
