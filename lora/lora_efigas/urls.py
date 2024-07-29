from django.urls import path
from .views import *

urlpatterns = [
    path('receive/', receive_data, name='receive-data'),
    path('api/device/valve/', ValveControl.as_view(), name='valve-control'),
    path('api/device/balance/', SetBalance.as_view(), name='set-balance'),
    path('api/device/consumption/', SetConsumption.as_view(), name='set-consumption'),
    path('api/devices/', LatestGasMeterDataView.as_view(), name='get-devices'),
    path('api/get-device/<str:deveui>/', GasMeterDataListView.as_view(), name='get-device'),
    path('api/device/time_report/', SetTime.as_view(), name='set-time'),
    path('api/device/query_temp/', QueryTemp.as_view(), name='query-temp'),
]
