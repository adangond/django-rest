#/patients/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from doctorapp.permissions import IsAdminUser, IsDoctorUser, IsPatientUser

class PatientPermission(BasePermission):
    """
    - Admin: todo permitido
    - Doctor: solo ver/listar si tiene cita con el paciente
    - Patient: solo ver/editar su propio registro
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (
                IsAdminUser().has_permission(request, view) or
                IsDoctorUser().has_permission(request, view) or
                IsPatientUser().has_permission(request, view)
            )
        )

    def has_object_permission(self, request, view, obj):
        # Admin siempre
        if IsAdminUser().has_permission(request, view):
            return True

        # Lectura abierta si consulta de lista o detalle
        if request.method in SAFE_METHODS:
            if IsDoctorUser().has_permission(request, view):
                # Ver paciente solo si doctor tiene cita con él
                return obj.appointments.filter(doctor__user=request.user).exists()
            if IsPatientUser().has_permission(request, view):
                # Paciente ve su propio perfil
                return obj.user == request.user
            return False

        # Escritura (PUT/PATCH/DELETE) solo paciente dueño o admin
        if IsPatientUser().has_permission(request, view):
            return obj.user == request.user

        return False