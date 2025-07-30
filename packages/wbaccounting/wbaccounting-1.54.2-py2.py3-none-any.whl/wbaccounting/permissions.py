from rest_framework.permissions import BasePermission


class IsInvoiceAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("wbaccounting.administrate_invoice")
