from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasChangeProjectPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (request.user.has_perm('projects.change_project') or
                request.user.has_perm('projects.change_project', view.project))


class HasCreateProjectConsentTokenPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('project_consents.add_projectconsenttoken')
