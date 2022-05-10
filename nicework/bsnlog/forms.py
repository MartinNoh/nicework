from django import forms
from .models import BusinessLog


class BusinessLogForm(forms.ModelForm):
    class Meta:
        model = BusinessLog
        fields = ['contents']