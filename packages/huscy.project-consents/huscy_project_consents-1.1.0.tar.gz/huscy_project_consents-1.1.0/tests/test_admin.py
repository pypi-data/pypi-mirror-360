import pytest
from model_bakery import baker

from django.contrib.admin.sites import AdminSite

from huscy.project_consents import admin, models, services

pytestmark = pytest.mark.django_db


@pytest.fixture
def project_consent_admin():
    return admin.ProjectConsentAdmin(models.ProjectConsent, AdminSite)


@pytest.fixture
def project_consent_category_admin():
    return admin.ProjectConsentCategoryAdmin(models.ProjectConsentCategory, AdminSite)


@pytest.fixture
def project_consent_file_admin():
    return admin.ProjectConsentFileAdmin(models.ProjectConsentFile, AdminSite)


@pytest.fixture
def project_consent_token_admin():
    return admin.ProjectConsentTokenAdmin(models.ProjectConsentToken, AdminSite)


@pytest.fixture
def project_intermediary_admin():
    return admin.ProjectIntermediaryAdmin(models.ProjectIntermediary, AdminSite)


def test_project_consent_admin_get_readonly_fields_on_create(request, project_consent_admin):
    assert () == project_consent_admin.get_readonly_fields(request)


def test_project_consent_admin_get_readonly_fields_on_update(request, project_consent_admin,
                                                             project_consent):
    assert ('project', ) == project_consent_admin.get_readonly_fields(request, project_consent)


def test_project_consent_admin_save_model_create(mocker, request, project_consent_admin,
                                                 project, text_fragments):
    project_consent = baker.prepare('project_consents.ProjectConsent',
                                    project=project,
                                    text_fragments=text_fragments)

    spy = mocker.spy(services, 'create_project_consent')

    project_consent_admin.save_model(request, project_consent, None, change=False)

    spy.assert_called_once_with(project, text_fragments)


def test_project_consent_admin_save_model_update(mocker, request, project_consent_admin,
                                                 project_consent, project):
    spy = mocker.spy(services, 'update_project_consent')

    project_consent_admin.save_model(request, project_consent, None, change=True)

    spy.assert_called_once_with(project_consent, project_consent.text_fragments)


def test_project_consent_category_admin_save_model_create(mocker, request,
                                                          project_consent_category_admin,
                                                          text_fragments):
    name = 'Project consent category name'
    project_consent_category = baker.prepare('project_consents.ProjectConsentCategory',
                                             name=name,
                                             template_text_fragments=text_fragments)

    spy = mocker.spy(services, 'create_project_consent_category')

    project_consent_category_admin.save_model(request, project_consent_category, None, change=False)

    spy.assert_called_once_with(name, text_fragments)


def test_project_consent_category_admin_save_model_update(mocker, request,
                                                          project_consent_category_admin,
                                                          project_consent_category):
    spy = mocker.spy(services, 'update_project_consent_category')

    project_consent_category_admin.save_model(request, project_consent_category, None, change=True)

    spy.assert_called_once_with(project_consent_category, project_consent_category.name,
                                project_consent_category.template_text_fragments)


def test_project_consent_file_admin(project_consent_file_admin, project_consent_file):
    project = project_consent_file.project_consent.project
    subject = project_consent_file.subject

    assert project.title == project_consent_file_admin._project(project_consent_file)
    assert subject.contact.display_name == project_consent_file_admin._subject(project_consent_file)


def test_project_consent_file_admin_has_change_permission(request, project_consent_file_admin,
                                                          project_consent_file):
    assert project_consent_file_admin.has_change_permission(request, project_consent_file) is False


def test_project_consent_file_admin_save_model(mocker, request, project_consent_file_admin,
                                               project_consent_file, project_consent, subject):
    spy = mocker.spy(services, 'create_project_consent_file')

    project_consent_file_admin.save_model(request, project_consent_file, form=None, change=False)

    filehandle = project_consent_file.filehandle
    spy.assert_called_once_with(project_consent, subject, filehandle)


def test_project_consent_token_admin(project_consent_token_admin, project_consent_token):
    project = project_consent_token.project
    subject = project_consent_token.subject

    assert project.title == project_consent_token_admin._project(project_consent_token)
    assert (subject.contact.display_name ==
            project_consent_token_admin._subject(project_consent_token))


def test_project_consent_token_admin_has_change_permission(request, project_consent_token_admin,
                                                           project_consent_token):
    assert project_consent_token_admin.has_change_permission(request,
                                                             project_consent_token) is False


def test_project_consent_token_admin_save_model(mocker, request, user, project_consent_token_admin,
                                                project_consent_token):
    project = project_consent_token.project
    subject = project_consent_token.subject

    spy = mocker.spy(services, 'create_project_consent_token')

    request.user = user
    project_consent_token_admin.save_model(request, project_consent_token, form=None, change=False)

    spy.assert_called_once_with(project, subject, user)


def test_project_intermediary_admin(project_intermediary_admin, project_intermediary):
    project = project_intermediary.project_membership.project
    user = project_intermediary.project_membership.user

    assert project.title == project_intermediary_admin._project(project_intermediary)
    assert user.username == project_intermediary_admin._username(project_intermediary)
