from django import forms

from .models import UserMasalaRelation


class UserMasalaRelationForm(forms.ModelForm):
    class Meta:
        model = UserMasalaRelation
        fields = ('language', 'script')