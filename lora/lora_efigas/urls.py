from django.urls import path
from .views import *

urlpatterns = [
    path('receive/', receive_data, name='receive-data'),
    path('api/device/valve/', ValveControl.as_view(), name='valve-control'),
]
