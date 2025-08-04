#/doctorapp/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsDoctorUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="doctor").exists()

class IsPatientUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="patient").exists()

class IsOwnerOrAdmin(BasePermission):
    """
    Permite lectura/escritura sólo al propietario del objeto o a staff.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # obj.user es el OneToOneField en Doctor/Patient
        return hasattr(obj, "user") and obj.user == request.user