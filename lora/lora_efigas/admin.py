from django.contrib import admin
from .models import GasMeterData

@admin.register(GasMeterData)
class GasMeterDataAdmin(admin.ModelAdmin):
    list_display = ['dev_eui', 'timestamp', 'accumulated_flow', 'total_flow', 'battery_voltage']
    list_filter = ['timestamp', 'dev_eui']
