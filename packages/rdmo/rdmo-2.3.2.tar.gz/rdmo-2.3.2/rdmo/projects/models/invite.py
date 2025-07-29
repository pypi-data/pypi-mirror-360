from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.crypto import salted_hmac
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ..constants import ROLE_CHOICES
from ..managers import InviteManager


class Invite(models.Model):

    key_salt = 'rdmo.projects.models.invite.Invite'

    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='invites',
        verbose_name=_('Project'),
        help_text=_('The project for this invite.')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        verbose_name=_('User'),
        help_text=_('The user for this membership.')
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_('E-mail'),
        help_text=_('The e-mail for this membership.')
    )
    role = models.CharField(
        max_length=12, choices=ROLE_CHOICES,
        verbose_name=_('Role'),
        help_text=_('The role for this invite.')
    )
    token = models.CharField(
        max_length=20,
        verbose_name=_('Token'),
        help_text=_('The token for this invite.')
    )
    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp'),
        help_text=_('The timestamp for this invite.')
    )

    objects = InviteManager()

    class Meta:
        ordering = ('timestamp', )
        verbose_name = _('Invite')
        verbose_name_plural = _('Invites')

    def __str__(self):
        return f'{self.project.title} / {self.email} / {self.role}'

    def save(self, *args, **kwargs):
        if self.timestamp is None:
            self.timestamp = now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project', kwargs={'pk': self.project.pk})

    @property
    def is_expired(self):
        if settings.PROJECT_INVITE_TIMEOUT:
            return (now() - self.timestamp).total_seconds() > settings.PROJECT_INVITE_TIMEOUT
        else:
            return False

    def make_token(self):
        self.token = salted_hmac(self.key_salt, self._make_hash_value()).hexdigest()[::2]

    def _make_hash_value(self):
        return str(self.project_id) + str(self.email) + str(self.role) + str(self.timestamp)
