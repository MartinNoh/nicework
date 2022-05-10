from django.urls import path
from .views import regt_views, hist_views


app_name = 'bsnlog'

urlpatterns = [
    path('regt/', regt_views.registration, name='regt'),
    path('hist/', hist_views.history, name='hist'),
    path('hist/<int:bsnlog_id>/', hist_views.update, name='updt'),
]