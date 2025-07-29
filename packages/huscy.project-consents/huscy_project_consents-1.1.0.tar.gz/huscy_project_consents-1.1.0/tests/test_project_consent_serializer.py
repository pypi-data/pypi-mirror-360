import pytest

from huscy.project_consents.serializer import ProjectConsentSerializer

pytestmark = pytest.mark.django_db


def test_project_consent_serializer_input_data(text_fragments):
    data = dict(text_fragments=text_fragments)
    serializer = ProjectConsentSerializer(data=data)
    assert serializer.is_valid()


def test_project_consent_serializer_output_data(project_consent):
    serializer = ProjectConsentSerializer(project_consent)
    assert serializer.data == {
        'id': project_consent.id,
        'project': project_consent.project.id,
        'text_fragments': project_consent.text_fragments,
        'version': 1,
    }
