import jsonschema

from . import models
from .constants import TEXT_FRAGMENTS_SCHEMA


def create_project_consent(project, text_fragments):
    jsonschema.validate(text_fragments, TEXT_FRAGMENTS_SCHEMA)
    return models.ProjectConsent.objects.create(project=project, text_fragments=text_fragments)


def create_project_consent_category(name, template_text_fragments):
    jsonschema.validate(template_text_fragments, TEXT_FRAGMENTS_SCHEMA)
    return models.ProjectConsentCategory.objects.create(
        name=name,
        template_text_fragments=template_text_fragments,
    )


def create_project_consent_file(project_consent, subject, filehandle):
    return models.ProjectConsentFile.objects.create(
        project_consent=project_consent,
        project_consent_version=project_consent.version,
        filehandle=filehandle,
        subject=subject,
    )


def create_project_consent_token(project, subject, creator):
    token, _created = models.ProjectConsentToken.objects.get_or_create(
        created_by=creator.get_full_name(),
        project=project,
        subject=subject,
    )
    return token


def create_project_intermediary(project_membership, email='', phone=''):
    return models.ProjectIntermediary.objects.create(
        email=email,
        phone=phone,
        project_membership=project_membership,
    )


def delete_project_intermediary(project_intermediary):
    project_intermediary.delete()


def update_project_consent(project_consent, text_fragments=None):
    if text_fragments is not None:
        jsonschema.validate(text_fragments, TEXT_FRAGMENTS_SCHEMA)
        project_consent.text_fragments = text_fragments
        project_consent.version += 1
        project_consent.save(update_fields=['text_fragments', 'version'])
    return project_consent


def update_project_consent_category(project_consent_category, name=None,
                                    template_text_fragments=None):
    update_fields = []

    if name is not None:
        project_consent_category.name = name
        update_fields.append('name')

    if (template_text_fragments is not None):
        jsonschema.validate(template_text_fragments, TEXT_FRAGMENTS_SCHEMA)
        project_consent_category.template_text_fragments = template_text_fragments
        update_fields.append('template_text_fragments')

    project_consent_category.save(update_fields=update_fields)

    return project_consent_category


def update_project_intermediary(project_intermediary, **kwargs):
    update_fields = []

    for field_name, value in kwargs.items():
        if field_name not in 'email phone'.split():
            raise ValueError(f'Cannot update field {field_name}')
        if getattr(project_intermediary, field_name) == value:
            continue
        setattr(project_intermediary, field_name, value)
        update_fields.append(field_name)

    if update_fields:
        project_intermediary.save(update_fields=update_fields)

    return project_intermediary
