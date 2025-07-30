from django.urls import re_path

from front_desk.views import (
    CashInvoicePayment, ChangeFoodView, ChangeShirtView, ChangeShoesView,
    CheckInView, CheckOutView, Dashboard, IssueInvoiceView, RegisterOnSite,
    RoomsView)


urlpatterns = [
    re_path(r'^$', Dashboard.as_view(), name='front_desk'),
    re_path(r'^check_in/(?P<username>[\w.@+-]+)/$', CheckInView.as_view(),
        name='front_desk.check_in'),
    re_path(r'^check_in/(?P<username>[\w.@+-]+)/change_shirt/$',
        ChangeShirtView.as_view(), name='front_desk.change_shirt'),
    re_path(r'^check_in/(?P<username>[\w.@+-]+)/change_shoes/$',
        ChangeShoesView.as_view(), name='front_desk.change_shoes'),
    re_path(r'^check_in/(?P<username>[\w.@+-]+)/change_food/$',
        ChangeFoodView.as_view(), name='front_desk.change_food'),
    re_path(r'^check_in/(?P<username>[\w.@+-]+)/invoice/$',
        IssueInvoiceView.as_view(), name='front_desk.invoice'),
    re_path(r'^register/$', RegisterOnSite.as_view(), name='front_desk.register'),
    re_path(r'^cash_payment/invoice/(?P<ref>[^/]+)/$',
        CashInvoicePayment.as_view(), name='front_desk.cash_invoice_payment'),
    re_path(r'^check_out/(?P<username>[\w.@+-]+)/$', CheckOutView.as_view(),
        name='front_desk.check_out'),
    re_path(r'^rooms$', RoomsView.as_view(), name='front_desk.rooms'),
]
