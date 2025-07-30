import uuid
from typing import List, Set
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.functional import cached_property
from .group import Group
from .permission import Permission
from ..db import CachedManager


class MemberManager(CachedManager):
    natural_key = ['tenant_id', 'user_id']

    def get_by_natural_key(self, tenant_id, user_id) -> 'Member':
        return self.get_from_cache_by_natural_key(tenant_id, user_id)


class Member(models.Model):
    class InviteStatus(models.IntegerChoices):
        REQUEST = 0, 'request'
        WAITING = 1, 'waiting'
        ACTIVE = 2, 'active'

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tenant = models.ForeignKey(settings.SAAS_TENANT_MODEL, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    # this email is only used for invitation
    invite_email = models.EmailField(null=True, blank=True)
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
    )

    status = models.SmallIntegerField(default=InviteStatus.REQUEST, choices=InviteStatus.choices)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions granted to each of their groups.'
        ),
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text=_('Specific permissions for this user.'),
    )
    objects = MemberManager()

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')
        unique_together = [
            ['tenant', 'user'],
        ]
        ordering = ['-created_at']
        db_table = 'saas_member'

    def __str__(self):
        if self.user:
            return str(self.user)
        if self.invite_email:
            return self.invite_email
        return ''

    @property
    def is_active(self) -> bool:
        return self.status == self.InviteStatus.ACTIVE

    @cached_property
    def group_permissions(self) -> List[str]:
        return self.__get_group_permissions()

    @cached_property
    def user_permissions(self) -> List[str]:
        return self.__get_user_permissions()

    def get_all_permissions(self) -> Set[str]:
        return set(self.user_permissions + self.group_permissions)

    def __get_group_permissions(self):
        return list(self.groups.values_list('permissions__name', flat=True))

    def __get_user_permissions(self):
        return list(self.permissions.all().values_list('name', flat=True))
