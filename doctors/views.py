from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from bookings.serializers import AppointmentSerializer
from bookings.models import Appointment
from patients.models import Patient

from .models import (
    Doctor,
    Department,
    DoctorAvailability,
    MedicalNote
)
from .serializers import (
    DoctorSerializer,
    DepartmentSerializer,
    DoctorAvailabilitySerializer,
    MedicalNoteSerializer
)
from .permissions import (
    IsDoctorOrReadOnly,
    IsDoctorOwnerOrAdmin
)


class DoctorViewSet(viewsets.ModelViewSet):
    """
    API para gestionar doctores.
      - list, retrieve: público.
      - create, update, delete: solo doctor propietario o admin.
      - appointments: acción custom para GET/POST de citas (solo usuarios autenticados).
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsDoctorOrReadOnly]

    @action(
        detail=True,
        methods=['get', 'post'],
        permission_classes=[IsAuthenticated]
    )
    def appointments(self, request, pk=None):
        doctor = self.get_object()

        # 1) Obtener el perfil de paciente desde request.user
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return Response(
                {"detail": _("Perfil de paciente no encontrado.")},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2) GET → devolver citas de este paciente con este doctor
        if request.method == 'GET':
            qs = Appointment.objects.filter(doctor=doctor, patient=patient)
            serializer = AppointmentSerializer(qs, many=True)
            return Response(serializer.data)

        # 3) POST → impedir si doctor está de vacaciones
        if doctor.is_on_vacation:
            return Response(
                {"detail": _("El doctor está de vacaciones.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4) POST → inyectar doctor y patient en el payload, crear cita
        data = request.data.copy()
        data['doctor'] = doctor.id
        data['patient'] = patient.id
        serializer = AppointmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API para departamentos médicos.
      - list, retrieve: público.
      - create, update, delete: solo admin.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    """
    API para disponibilidad de doctores.
      - list, retrieve: público.
      - create, update, delete: solo doctor propietario o admin.
    """
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsDoctorOwnerOrAdmin()]
        return [AllowAny()]


class MedicalNoteViewSet(viewsets.ModelViewSet):
    """
    API para notas médicas.
      - list, retrieve, create, update, delete: solo doctor propietario o admin.
    """
    queryset = MedicalNote.objects.all()
    serializer_class = MedicalNoteSerializer

    def get_permissions(self):
        if self.action in [
            'list', 'retrieve',
            'create', 'update', 'partial_update', 'destroy'
        ]:
            return [IsAuthenticated(), IsDoctorOwnerOrAdmin()]
        return [AllowAny()]