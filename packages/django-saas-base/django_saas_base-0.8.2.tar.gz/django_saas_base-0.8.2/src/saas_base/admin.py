from django.contrib import admin
from .models import (
    Permission,
    Group,
    Member,
    UserEmail,
    Tenant,
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'internal', 'created_at']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug', 'owner', 'expires_at', 'created_at']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'tenant', 'name', 'managed', 'created_at']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'tenant', 'user', 'invite_email', 'status', 'created_at']


@admin.register(UserEmail)
class UserEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'primary', 'verified', 'created_at']
