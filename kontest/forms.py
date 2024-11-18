from django import forms

from .models import UserMasalaRelation


class UserMasalaRelationForm(forms.ModelForm):
    code = forms.CharField(strip=False, widget=forms.Textarea({'required': False}))

    class Meta:
        model = UserMasalaRelation
        fields = ('language', 'script', 'code')

