from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from ..models import get_tenant_model, Member
from ..settings import saas_settings

__all__ = [
    'IsTenantOwner',
    'IsTenantOwnerOrReadOnly',
    'HasResourcePermission',
    'HasResourceScope',
]

TenantModel = get_tenant_model()

http_method_actions = {
    'GET': 'read',
    'HEAD': 'read',
    'POST': 'write',
    'PUT': 'write',
    'PATCH': 'write',
    'DELETE': 'admin',
}


class IsTenantOwner(BasePermission):
    """The authenticated user is the tenant owner."""

    def has_permission(self, request: Request, view):
        tenant_id = getattr(request, 'tenant_id', None)
        if not tenant_id:
            return False
        try:
            tenant = TenantModel.objects.get_from_cache_by_pk(tenant_id)
            return request.user.pk == tenant.owner_id
        except TenantModel.DoesNotExist:
            return False


class IsTenantOwnerOrReadOnly(IsTenantOwner):
    """The authenticated user is the tenant owner, or is a read-only request."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class HasResourcePermission(BasePermission):
    """The authenticated user is a member of the tenant, and the user
    has the given resource permission.
    """

    @staticmethod
    def get_resource_permissions(view, method):
        handler = getattr(view, method.lower(), None)
        if not handler:
            return None

        permissions = getattr(handler, '_resource_permissions', None)
        if permissions:
            return permissions

        resource = getattr(view, 'resource_name', None)
        if not resource:
            return None

        action = getattr(view, 'resource_action', None)
        if not action:
            method_actions = getattr(view, 'resource_http_method_actions', http_method_actions)
            action = method_actions.get(method)

        permission = saas_settings.PERMISSION_NAME_FORMATTER.format(
            resource=resource,
            action=action,
        )
        return [permission]

    @staticmethod
    def get_tenant(request: Request):
        tenant_id = getattr(request, 'tenant_id', None)
        if not tenant_id:
            return None
        try:
            return TenantModel.objects.get_from_cache_by_pk(tenant_id)
        except TenantModel.DoesNotExist:
            return None

    def has_permission(self, request: Request, view):
        resource_permissions = self.get_resource_permissions(view, request.method)
        if not resource_permissions:
            return True

        # HasResourcePermission should apply to TenantEndpoint
        tenant = self.get_tenant(request)
        if not tenant:
            return False

        # Tenant owner has all permissions
        if tenant.owner_id == request.user.pk:
            return True

        try:
            member = Member.objects.get_by_natural_key(tenant.pk, request.user.pk)
            if not member.is_active:
                return False
        except Member.DoesNotExist:
            return False

        perms = member.get_all_permissions()
        if not perms:
            return False

        return bool(set(resource_permissions) & perms)


class HasResourceScope(BasePermission):
    """The request token contains the given resource scopes."""

    @staticmethod
    def get_resource_scopes(view, method):
        if hasattr(view, 'get_resource_scopes'):
            resource_scopes = view.get_resource_scopes(method)
        elif hasattr(view, 'resource_scopes'):
            resource_scopes = view.resource_scopes
        else:
            resource_scopes = None
        return resource_scopes

    def has_permission(self, request: Request, view):
        resource_scopes = self.get_resource_scopes(view, request.method)
        if not resource_scopes:
            return True

        if request.auth is None:
            return True

        scope = getattr(request.auth, 'scope', '')
        if scope == '__all__':
            return True

        token_scopes = set(scope.split())
        for rs in resource_scopes:
            if set(rs.split()).issubset(token_scopes):
                return True
        return False
