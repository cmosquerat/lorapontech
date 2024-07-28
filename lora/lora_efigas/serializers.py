from rest_framework import serializers
from .models import GasMeterData

class GasMeterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasMeterData
        fields = '__all__'  # You can specify fields you want to include
