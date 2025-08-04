#/patients/serializers.py

from rest_framework import serializers
from .models import Patient, Insurance, MedicalRecord

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

    def validate_user(self, value):
        user = self.context['request'].user
        if user.is_staff:
            return value
        if user != value:
            raise serializers.ValidationError("No puedes modificar el perfil de otro paciente.")
        return value


class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = '__all__'

    def validate_patient(self, value):
        user = self.context['request'].user
        if user.is_staff:
            return value
        if not hasattr(user, 'patient'):
            raise serializers.ValidationError("Solo los pacientes pueden registrar seguros.")
        if user.patient != value:
            raise serializers.ValidationError("No puedes registrar seguros para otro paciente.")
        return value


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

    def validate_patient(self, value):
        user = self.context['request'].user
        if user.is_staff:
            return value
        if not hasattr(user, 'patient'):
            raise serializers.ValidationError("Solo los pacientes pueden registrar historial médico.")
        if user.patient != value:
            raise serializers.ValidationError("No puedes registrar historial para otro paciente.")
        return value
