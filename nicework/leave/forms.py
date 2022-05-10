from django import forms
from .models import Leave


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['reason', 'startdate', 'enddate', 'leavecat', 'starttime', 'endtime', 'emgnum']