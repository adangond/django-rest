#/doctors/modepermissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsDoctorOrReadOnly(BasePermission):
    """
    Read-only for any authenticated user.
    Write (POST/PUT/PATCH/DELETE) only for doctors or admins.
    """
    def has_permission(self, request, view):
        # Always allow safe methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Only authenticated doctors or staff can write
        user = request.user
        return bool(
            user and
            user.is_authenticated and
            (user.is_staff or hasattr(user, 'doctor'))
        )

    def has_object_permission(self, request, view, obj):
        # Safe methods: allowed if has permission above
        if request.method in SAFE_METHODS:
            return True

        # Staff can do anything
        if request.user.is_staff:
            return True

        # Doctors can only modify their own record
        if hasattr(request.user, 'doctor'):
            return obj.user == request.user

        return False


class IsDoctorOwnerOrAdmin(BasePermission):
    """
    Only the doctor themself or an admin can modify/delete.
    Read access still governed by IsDoctorOrReadOnly.
    """
    def has_permission(self, request, view):
        # Must be authenticated for any write action
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Admin can always
        if request.user.is_staff:
            return True

        # Doctor can if they own the object
        if hasattr(request.user, 'doctor'):
            return obj.user == request.user

        return False