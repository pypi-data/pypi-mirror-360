import yaml
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand


from volunteers.models import TaskCategory, TaskTemplate, Task
from wafer.schedule.models import Venue


class Command(BaseCommand):
    help = 'Creates volunteer tasks from a YAML file'

    def add_arguments(self, parser):
        parser.add_argument('FILE', type=open)

    def handle(self, *args, **options):
        data = yaml.safe_load(options['FILE'])

        created_items = {
            'categories': 0,
            'tasks': 0,
            'templates': 0,
            'venues': 0,
        }
        for item in data['tasks']:
            category, created = TaskCategory.objects.get_or_create(
                name=item['category'])
            if created:
                print('Created category:', category)
                created_items['categories'] += 1

            template, created = TaskTemplate.objects.update_or_create(
                name=item['name'],
                defaults={
                    'nbr_volunteers_min': item.get('nbr_volunteers_min', None),
                    'nbr_volunteers_max': item.get('nbr_volunteers_max', None),
                    'description': item.get('description', None),
                    'video_task': item.get('video_task', False),
                    'required_permission': item.get('required_permission', None),
                })
            if created:
                print('Created template:', template)
                created_items['templates'] += 1

            if 'venues' in item:
                venues = []
                for v in item['venues']:
                    venue, created = Venue.objects.get_or_create(name=v)
                    if created:
                        print('Created venue:', venue)
                        created_items['venues'] += 1
                    venues.append(venue)
            else:
                venues = [None]

            if item.get('video_task', False):
                if 'specs' in item or 'days' in item:
                    raise Exception("Tasks can't have video_task and specs/days")
                continue

            task_specs = []
            if 'days' in item:
                task_specs.append(item)
            if 'specs' in item:
                task_specs.extend(item['specs'])

            for spec in task_specs:
                for day in spec['days']:
                    for hour in spec['hours']:
                        startstr = hour['start']
                        start = timezone.make_aware(
                            datetime.strptime('%s %s' % (day, startstr), '%Y-%m-%d %H:%M')
                        )
                        if 'end' in hour:
                            endstr = hour['end']
                            end = timezone.make_aware(
                                datetime.strptime('%s %s' % (day, endstr), '%Y-%m-%d %H:%M')
                            )
                        else:
                            duration = hour['duration']
                            end = start + timedelta(minutes=duration)

                        for venue in venues:
                            task, created = Task.objects.get_or_create(
                                template=template,
                                start=start,
                                end=end,
                                venue=venue,
                            )
                            if created:
                                print('Created task:', task)
                                created_items['tasks'] += 1
        print('Created: {categories} categories, {templates} templates, '
              '{venues} venues, and {tasks} tasks.'.format(**created_items))
