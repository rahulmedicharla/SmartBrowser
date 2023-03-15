from django import forms
from .models import Temp

class TempInputForm(forms.ModelForm):
    class Meta: 
        model = Temp
        fields = ['text_input']