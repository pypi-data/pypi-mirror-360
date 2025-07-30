from django.urls import re_path

from invoices.views import (
    InvoiceCancel, InvoiceCombine, InvoiceDisplay, stripe_webhook)

app_name = 'invoices'
urlpatterns = [
    re_path(r'^combine/$', InvoiceCombine.as_view(), name='combine'),
    re_path(r'^stripe-webhook/$', stripe_webhook),
    re_path(r'^(?P<reference_number>[^/]+)/$', InvoiceDisplay.as_view(),
        name='display'),
    re_path(r'^(?P<reference_number>[^/]+)/cancel/$', InvoiceCancel.as_view(),
        name='cancel'),
]
