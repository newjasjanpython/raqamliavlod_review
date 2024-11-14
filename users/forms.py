from django.contrib.auth.forms import UserCreationForm as UCF
from django import forms

from .models import User


class UserCreationForm(UCF):
    first_name = forms.CharField(max_length=100, help_text="Ismni kiriting", label="Ismni kiriting", widget=forms.TextInput({'placeholder':'Ism'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name','username','email', 'telefon', 'viloyat', 'tuman', 'maktab')
