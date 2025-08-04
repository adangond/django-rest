#/doctors/serializers.py

from rest_framework import serializers
from .models import Doctor, Department, DoctorAvailability, MedicalNote

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = '__all__'

    def validate_doctor(self, value):
        user = self.context['request'].user
        if user.is_staff:
            return value
        if not hasattr(user, 'doctor'):
            raise serializers.ValidationError("Solo los doctores pueden modificar disponibilidad.")
        if user.doctor != value:
            raise serializers.ValidationError("No puedes modificar la disponibilidad de otro doctor.")
        return value


class MedicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalNote
        fields = '__all__'

    def validate_doctor(self, value):
        user = self.context['request'].user
        if user.is_staff:
            return value
        if not hasattr(user, 'doctor'):
            raise serializers.ValidationError("Solo los doctores pueden crear notas médicas.")
        if user.doctor != value:
            raise serializers.ValidationError("No puedes crear notas médicas en nombre de otro doctor.")
        return value