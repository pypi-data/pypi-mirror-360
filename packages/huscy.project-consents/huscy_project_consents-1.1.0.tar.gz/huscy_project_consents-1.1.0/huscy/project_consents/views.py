import re
import string
import unicodedata

from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views import generic
from weasyprint import HTML

from . import forms, models, services


def sanitize_string(_string):
    # replace umlauts
    _string = re.sub('[ä]', 'ae', _string)
    _string = re.sub('[Ä]', 'Ae', _string)
    _string = re.sub('[ö]', 'oe', _string)
    _string = re.sub('[Ö]', 'Oe', _string)
    _string = re.sub('[ü]', 'ue', _string)
    _string = re.sub('[Ü]', 'Ue', _string)
    _string = re.sub('[ß]', 'ss', _string)

    # remove accents
    _string = ''.join(c for c in unicodedata.normalize('NFKD', _string)
                      if not unicodedata.combining(c))

    # remove punctuation
    _string = _string.translate(str.maketrans('', '', string.punctuation))

    return _string


class SignProjectConsentView(generic.FormView):
    form_class = formset_factory(forms.SignatureForm, extra=2)
    template_name = 'project_consents/sign_project_consent.html'

    def dispatch(self, request, *args, **kwargs):
        self.token = get_object_or_404(models.ProjectConsentToken, pk=self.kwargs['token'])
        self.project = self.token.project
        self.subject = self.token.subject
        self.project_consent = self.project.projectconsent
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_intermediaries = models.ProjectIntermediary.objects.filter(
            project_membership__project=self.project,
        )

        context.update({
            'consent': self.project_consent,
            'experimenter': self.token.created_by,
            'project': self.project,
            'project_intermediaries': project_intermediaries,
            'subject': self.subject,
        })
        return context

    def form_valid(self, form):
        html_template = get_template('project_consents/signed_project_consent.html')

        custom_data = dict((key, value)
                           for key, value in self.request.POST.items()
                           if key.startswith('textfragment'))

        context = self.get_context_data()
        context.update({
            'custom_data': custom_data,
            'form': form,
        })
        rendered_html = html_template.render(context)

        content = HTML(string=rendered_html, base_url=self.request.build_absolute_uri()).write_pdf()

        filename = '_'.join([
            *sanitize_string(self.subject.contact.display_name).split(),
            self.subject.contact.date_of_birth.strftime('%Y%m%d')
        ]) + '.pdf'
        filehandle = SimpleUploadedFile(
            name=filename,
            content=content,
            content_type='application/pdf'
        )
        services.create_project_consent_file(
            filehandle=filehandle,
            project_consent=self.project_consent,
            subject=self.subject,
        )

        self.token.delete()

        return HttpResponse(content, content_type='application/pdf')
