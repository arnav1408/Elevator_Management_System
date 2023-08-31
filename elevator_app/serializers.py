from rest_framework import serializers
from .models import Elevator

class ElevatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elevator
        fields = '__all__'
