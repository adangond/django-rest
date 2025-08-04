#/booking/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Appointment, MedicalNote
from .serializers import AppointmentSerializer, MedicalNoteSerializer
from .permissions import IsBookingOrReadOnly, IsBookingOwnerOrAdmin


# 📅 ViewSet para gestionar citas médicas
class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API para gestionar citas médicas.

    - list, retrieve:
        Sólo lectura para usuarios autenticados (IsBookingOrReadOnly).
    - create:
        El paciente propietario o un admin pueden agendar una cita (IsBookingOwnerOrAdmin).
    - update, partial_update, destroy:
        El paciente o el doctor asignado, o un admin pueden modificar o cancelar la cita (IsBookingOwnerOrAdmin).
    - medical_notes (GET @ /appointments/{pk}/medical-notes):
        El paciente o doctor propietario, o un admin pueden consultar las notas asociadas (IsBookingOwnerOrAdmin).
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsBookingOrReadOnly]

    def get_permissions(self):
        protected = [
            'create',
            'update', 'partial_update', 'destroy',
            'medical_notes'
        ]
        if self.action in protected:
            return [IsBookingOwnerOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['get'], url_path='medical-notes')
    def medical_notes(self, request, pk=None):
        """
        Devuelve todas las notas médicas asociadas a una cita.
        Sólo el paciente o doctor propietario, o un admin pueden acceder.
        """
        appointment = self.get_object()
        notes = appointment.medical_notes.all()
        serialized = MedicalNoteSerializer(notes, many=True).data

        return Response({
            "appointment_id":    appointment.id,
            "doctor":            str(appointment.doctor),
            "patient":           str(appointment.patient),
            "appointment_date":  appointment.appointment_date,
            "appointment_time":  appointment.appointment_time,
            "status":            appointment.status,
            "medical_notes":     serialized
        })


# 📝 ViewSet para gestionar notas médicas asociadas a citas
class MedicalNoteViewSet(viewsets.ModelViewSet):
    """
    API para gestionar notas médicas de citas.

    - list, retrieve:
        Sólo lectura para usuarios autenticados (IsBookingOrReadOnly).
    - create, update, partial_update, destroy:
        Sólo el doctor autor de la nota o un admin pueden operar (IsBookingOwnerOrAdmin).
    """
    queryset = MedicalNote.objects.all()
    serializer_class = MedicalNoteSerializer
    permission_classes = [IsBookingOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBookingOwnerOrAdmin()]
        return super().get_permissions()
