from django.urls import path

from .views import regt_views, hist_views

app_name = 'commute'

urlpatterns = [    
    path('regt/<str:check_result>/', regt_views.registration, name='regt'),    

    path('hist/', hist_views.history, name='hist'),
    path('situ/', hist_views.situation, name='situ'),
    path('toth/', hist_views.totalhistory, name='toth'),
]