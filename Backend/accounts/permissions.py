"""Role-based permissions for PHARVO.

Roles are enforced on the server, never trusted from the client. The two
staff-facing roles (admin, pharmacist) and legacy ``is_staff`` users share
pharmacy access; the ``customer`` role is restricted to its own portal.
"""

from rest_framework import permissions

from .models import User

PHARMACY_ROLES = (User.Role.ADMIN, User.Role.PHARMACIST)


def is_pharmacy_staff(user):
    """True for admin, pharmacist and legacy staff users."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return getattr(user, "role", None) in PHARMACY_ROLES


class IsPharmacyStaff(permissions.BasePermission):
    """Allow only pharmacy personnel (admin, pharmacist, or staff)."""

    message = "Pharmacy staff access required."

    def has_permission(self, request, view):
        return is_pharmacy_staff(request.user)


class IsAdmin(permissions.BasePermission):
    """Allow only users with the ``admin`` role."""

    message = "Administrator access required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.ADMIN
        )


class IsCustomer(permissions.BasePermission):
    """Allow only users with the ``customer`` role."""

    message = "Customer access required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.CUSTOMER
        )


class IsStaffOrReadOnly(permissions.BasePermission):
    """Pharmacy staff may read; writes require Django staff privileges."""

    def has_permission(self, request, view):
        if not is_pharmacy_staff(request.user):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_staff)
