import json

from django import forms
from jsignature.forms import JSignatureField


class SignatureForm(forms.Form):
    signature = JSignatureField()

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        return json.dumps(signature)
