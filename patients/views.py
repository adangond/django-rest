#/patients/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Patient, Insurance, MedicalRecord
from .serializers import (
    PatientSerializer,
    InsuranceSerializer,
    MedicalRecordSerializer,
)
from .permissions import PatientPermission


class PatientViewSet(viewsets.ModelViewSet):
    """
    API para gestionar pacientes y consultar su historia clínica.

    - list:
        Usuarios autenticados (staff, médicos, pacientes) ven sólo los pacientes
        que les corresponden, según su rol.
    - retrieve:
        Solo el paciente dueño o staff.
    - create:
        Cualquier usuario autenticado puede registrar un nuevo paciente.
    - update / partial_update / destroy:
        Solo el paciente dueño o staff.
    - clinical_history (GET /patients/{pk}/clinical-history/):
        Solo el paciente dueño o staff.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, PatientPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Patient.objects.all()

        if hasattr(user, 'doctor'):
            return (
                Patient.objects
                .filter(appointments__doctor__user=user)
                .distinct()
            )

        if hasattr(user, 'patient'):
            return Patient.objects.filter(user=user)

        return Patient.objects.none()

    @action(
        detail=True,
        methods=['get'],
        url_path='clinical-history',
        permission_classes=[IsAuthenticated, PatientPermission]
    )
    def clinical_history(self, request, pk=None):
        """
        Devuelve un reporte con datos personales, seguros y registros médicos.
        """
        patient = self.get_object()
        insurances = patient.insurances.all().values(
            'provider', 'policy_number', 'expiration_date'
        )
        records = patient.medical_records.all().values(
            'date', 'diagnosis', 'treatment', 'follow_up_date'
        )
        report = {
            "patient": {
                "id": patient.id,
                "full_name": f"{patient.first_name} {patient.last_name}",
                "date_of_birth": patient.date_of_birth,
                "contact_number": patient.contact_number,
                "email": patient.email,
                "address": patient.address,
                "medical_history": patient.medical_history,
            },
            "insurances": list(insurances),
            "medical_records": list(records),
        }
        return Response(report)


class InsuranceViewSet(viewsets.ModelViewSet):
    """
    API para gestionar seguros de pacientes.

    - list, retrieve:
        Lectura para pacientes dueño, médicos a cargo o staff.
    - create, update, partial_update, destroy:
        Solo el paciente dueño o staff.
    """
    serializer_class = InsuranceSerializer
    permission_classes = [IsAuthenticated, PatientPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Insurance.objects.all()

        if hasattr(user, 'doctor'):
            return Insurance.objects.filter(
                patient__appointments__doctor__user=user
            ).distinct()

        if hasattr(user, 'patient'):
            return Insurance.objects.filter(patient=user.patient)

        return Insurance.objects.none()


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    API para gestionar registros médicos de pacientes.

    - list, retrieve:
        Lectura para pacientes dueño, médicos a cargo o staff.
    - create, update, partial_update, destroy:
        Solo el paciente dueño o staff.
    """
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated, PatientPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return MedicalRecord.objects.all()

        if hasattr(user, 'doctor'):
            return MedicalRecord.objects.filter(
                patient__appointments__doctor__user=user
            ).distinct()

        if hasattr(user, 'patient'):
            return MedicalRecord.objects.filter(patient=user.patient)

        return MedicalRecord.objects.none()