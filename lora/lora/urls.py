from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lora_efigas/', include('lora_efigas.urls')),
]
