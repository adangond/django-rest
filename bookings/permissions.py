#/bookings/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBookingOrReadOnly(BasePermission):
    """
    - SAFE_METHODS (GET, HEAD, OPTIONS):
        Lectura para cualquier usuario autenticado.
    - create:
        Solo pacientes (o admins) pueden agendar nuevas citas.
    - update/partial_update/destroy:
        Permitidos a nivel objeto, delegados a IsBookingOwnerOrAdmin.
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # Crear: pacientes o staff/admin
        if view.action == 'create':
            return user.is_staff or hasattr(user, 'patient')

        # SAFE_METHODS: lista y detalle
        if request.method in SAFE_METHODS:
            return True

        # PUT/PATCH/DELETE: permiso a nivel objeto
        return True

    def has_object_permission(self, request, view, obj):
        # Lectura (SAFE_METHODS):
        if request.method in SAFE_METHODS:
            if request.user.is_staff:
                return True
            if hasattr(request.user, 'patient'):
                return obj.patient.user == request.user
            if hasattr(request.user, 'doctor'):
                return obj.doctor.user == request.user
            return False

        # Escritura (PUT/PATCH/DELETE): delegamos a OwnerOrAdmin
        return IsBookingOwnerOrAdmin().has_object_permission(request, view, obj)


class IsBookingOwnerOrAdmin(BasePermission):
    """
    Solo el paciente dueño, el doctor a cargo o el admin pueden modificar o eliminar.
    """
    def has_permission(self, request, view):
        # Solo usuarios autenticados
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin siempre
        if user.is_staff:
            return True

        # Paciente dueño de la cita
        if hasattr(user, 'patient') and obj.patient.user == user:
            return True

        # Doctor asociado a la cita
        if hasattr(user, 'doctor') and obj.doctor.user == user:
            return True

        return False