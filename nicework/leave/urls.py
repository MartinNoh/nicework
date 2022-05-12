from django.urls import path

from .views import regt_views, hist_views

app_name = 'leave'

urlpatterns = [
    path('regt/', regt_views.registration, name='regt'),

    path('hist/', hist_views.history, name='hist'),
    path('wait/', hist_views.waiting, name='wait'),
    path('toth/', hist_views.totalhistory, name='toth'),
]