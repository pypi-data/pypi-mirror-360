import pytest
from pytest_bdd import scenarios, when

from rest_framework.reverse import reverse

scenarios('features')

pytestmark = pytest.mark.django_db


@when('I try to create a project consent token', target_fixture='request_result')
def create_project_consent_token(client, project_consent, subject):
    return client.post(
        reverse('projectconsent-token', kwargs=dict(project_pk=project_consent.project.pk,
                                                    pk=project_consent.pk)),
        data=dict(subject=subject.id)
    )
