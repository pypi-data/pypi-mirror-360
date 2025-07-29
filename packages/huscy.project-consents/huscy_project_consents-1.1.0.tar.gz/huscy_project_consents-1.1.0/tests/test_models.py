import pytest
from model_bakery import baker

from huscy.project_consents.models import ProjectConsentFile

pytestmark = pytest.mark.django_db


def test_project_consent_category_str_method():
    project_consent_category = baker.prepare('project_consents.ProjectConsentCategory',
                                             name='Project consent category name')

    assert str(project_consent_category) == 'Project consent category name'


def test_project_consent_str_method():
    project_consent = baker.prepare('project_consents.ProjectConsent', version=3,
                                    project__title='Project title')

    assert str(project_consent) == 'Project title (version: 3)'


def test_get_consent_file_upload_path():
    project_consent = baker.make('project_consents.ProjectConsent')
    project_consent_file = baker.prepare('project_consents.ProjectConsentFile',
                                         project_consent=project_consent)

    result = ProjectConsentFile.get_upload_path(project_consent_file, 'filename.pdf')

    assert f'projects/{project_consent.project.id}/consents/filename.pdf' == result
