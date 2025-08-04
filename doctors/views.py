#/doctors/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser,
    AllowAny,
    IsAuthenticated
)
from rest_framework.response import Response

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
    - Cualquiera puede listar y ver detalles.
    - Solo un admin puede crear un doctor.
    - El doctor dueño o un admin puede actualizar o borrar su perfil.
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_permissions(self):
        # Solo admin crea doctores
        if self.action == 'create':
            perms = [IsAdminUser]
        # Solo dueño o admin puede modificar o borrar
        elif self.action in ['update', 'partial_update', 'destroy']:
            perms = [IsAuthenticated, IsDoctorOwnerOrAdmin]
        # Lectura pública
        else:
            perms = [AllowAny]
        return [p() for p in perms]


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API para departamentos médicos.
    - Todos pueden listar y ver detalles.
    - Solo admin crea, actualiza o borra.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class DoctorAvailabilityViewSet(viewsets.ModelViewSet):
    """
    API para disponibilidad de doctores.
    - Cualquiera puede consultar (list, retrieve).
    - Solo el doctor dueño o un admin puede crear, actualizar o borrar su disponibilidad.
    """
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer

    def get_permissions(self):
        # Crear, modificar o borrar solo dueño o admin
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            perms = [IsAuthenticated, IsDoctorOwnerOrAdmin]
        # Listado y detalle son de lectura pública
        else:
            perms = [AllowAny]
        return [p() for p in perms]


class MedicalNoteViewSet(viewsets.ModelViewSet):
    """
    API para notas médicas.
    - Solo el doctor dueño o un admin puede listar, ver, crear, actualizar o borrar notas.
    - No hay endpoints de lectura pública.
    """
    queryset = MedicalNote.objects.all()
    serializer_class = MedicalNoteSerializer

    def get_permissions(self):
        # Todas las operaciones CRUD solo para dueño o admin
        if self.action in [
            'list', 'retrieve',
            'create', 'update',
            'partial_update', 'destroy'
        ]:
            perms = [IsAuthenticated, IsDoctorOwnerOrAdmin]
        else:
            # HEAD, OPTIONS...
            perms = [AllowAny]
        return [p() for p in perms]