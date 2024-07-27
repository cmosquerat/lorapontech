from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

###################### GUARDAR DATOS ##################


class GasMeterData(models.Model):
    dev_eui = models.CharField(max_length=16, verbose_name='Device EUI')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    accumulated_flow = models.IntegerField(verbose_name='Accumulated Flow (L)')
    total_flow = models.IntegerField(verbose_name='Total Flow (L)')
    meter_status = models.IntegerField(verbose_name='Meter Status')
    alarm = models.IntegerField(verbose_name='Alarm')
    battery_voltage = models.FloatField(verbose_name='Battery Voltage (V)')
    rssi = models.IntegerField(verbose_name='RSSI')
    snr = models.IntegerField(verbose_name='SNR')

    def __str__(self):
        return f"{self.dev_eui} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Gas Meter Data'
        verbose_name_plural = 'Gas Meter Data'


