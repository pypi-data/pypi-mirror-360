from django.urls import re_path

from volunteers.views import (
    TaskView, TasksView, VideoMassScheduleView, VideoShirtView,
    VolunteerStatisticsView, VolunteerView, VolunteerUpdate,
)

urlpatterns = [
    re_path(r'^$', TasksView.as_view(), name='wafer_tasks'),
    re_path(r'^tasks/(?P<pk>\d+)/$', TaskView.as_view(), name='wafer_task'),
    re_path(r'^statistics/$', VolunteerStatisticsView.as_view(),
        name='wafer_volunteer_statistics'),
    re_path(r'^(?P<slug>[\w.@+-]+)/$', VolunteerView.as_view(),
        name='wafer_volunteer'),
    re_path(r'^(?P<slug>[\w.@+-]+)/update/$', VolunteerUpdate.as_view(),
        name='wafer_volunteer_update'),
    re_path(r'^admin/video_mass_schedule/$', VideoMassScheduleView.as_view(),
        name='wafer_volunteer_video_mass_schedule'),
    re_path(r'^admin/video_shirts/$', VideoShirtView.as_view(),
        name='wafer_volunteer_video_shirt'),
]
