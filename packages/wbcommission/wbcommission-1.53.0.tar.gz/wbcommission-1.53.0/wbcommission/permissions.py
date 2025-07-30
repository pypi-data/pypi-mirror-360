from rest_framework.permissions import BasePermission


class IsCommissionAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("wbcommission.administrate_commission")
