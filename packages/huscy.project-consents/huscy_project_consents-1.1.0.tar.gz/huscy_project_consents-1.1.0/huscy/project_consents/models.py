import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from huscy.projects.models import Project, Membership
from huscy.subjects.models import Subject


class ProjectConsentCategory(models.Model):
    name = models.CharField(_('Name'), max_length=255, unique=True)
    template_text_fragments = models.JSONField(_('Template text fragments'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = 'name',
        verbose_name = _('Project consent category')
        verbose_name_plural = _('Project consent categories')


class ProjectConsent(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, verbose_name=_('Project'))
    text_fragments = models.JSONField(_('Text fragments'))
    version = models.PositiveSmallIntegerField(_('Version'), editable=False, default=1)

    def __str__(self):
        return f'{self.project.title} (version: {self.version})'

    class Meta:
        verbose_name = _('Project consent')
        verbose_name_plural = _('Project consents')


class ProjectConsentToken(models.Model):
    id = models.UUIDField(_('ID'), primary_key=True, editable=False, default=uuid.uuid4)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('Project'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_('Subject'))

    created_at = models.DateTimeField(_('Created at'), auto_now_add=True, editable=False)
    created_by = models.CharField(_('Created by'), max_length=255, editable=False)

    class Meta:
        verbose_name = _('Project consent token')
        verbose_name_plural = _('Project consent tokens')


class ProjectConsentFile(models.Model):

    def get_upload_path(self, filename):
        project = self.project_consent.project
        return f'projects/{project.id}/consents/{filename}'

    project_consent = models.ForeignKey(ProjectConsent, on_delete=models.CASCADE,
                                        verbose_name=_('Project consent'))
    project_consent_version = models.PositiveIntegerField(_('Project consent version'),
                                                          editable=False)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_('Subject'))

    filehandle = models.FileField(_('Filehandle'), upload_to=get_upload_path)

    created_at = models.DateTimeField(_('Created at'), auto_now_add=True, editable=False)

    class Meta:
        unique_together = 'project_consent', 'project_consent_version', 'subject'
        verbose_name = _('Project consent file')
        verbose_name_plural = _('Project consent files')


class ProjectIntermediary(models.Model):
    project_membership = models.OneToOneField(Membership, on_delete=models.CASCADE,
                                              verbose_name=_('Project membership'))

    email = models.EmailField(_('Email'), blank=True, default='')
    phone = PhoneNumberField(_('Phone'), blank=True, default='')

    class Meta:
        verbose_name = _('Project intermediary')
        verbose_name_plural = _('Project intermediaries')
