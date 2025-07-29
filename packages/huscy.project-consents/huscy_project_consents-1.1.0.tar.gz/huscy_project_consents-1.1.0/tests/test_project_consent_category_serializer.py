import pytest

from huscy.project_consents.serializer import ProjectConsentCategorySerializer

pytestmark = pytest.mark.django_db


def test_project_consent_category_serializer_input_data(text_fragments):
    data = dict(name='consent category name', template_text_fragments=text_fragments)
    serializer = ProjectConsentCategorySerializer(data=data)
    assert serializer.is_valid()


def test_project_consent_category_serializer_output_data(project_consent_category):
    serializer = ProjectConsentCategorySerializer(project_consent_category)
    assert serializer.data == {
        'id': project_consent_category.id,
        'name': project_consent_category.name,
        'template_text_fragments': project_consent_category.template_text_fragments,
    }
