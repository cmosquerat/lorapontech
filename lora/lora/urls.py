from django.contrib import admin
from django.urls import include, path
from .views import home 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('lora_efigas/', include('lora_efigas.urls')),
    path('', home, name='home')
]
print(admin.site.urls,include('lora_efigas.urls'))