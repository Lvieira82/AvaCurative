from django import forms
from .models import Paciente


class PacienteForm(forms.ModelForm):

    class Meta:
        model = Paciente
        fields = [
            'nome',
            'endereco',
            'telefone',
            'data_nascimento',
            'origem',
            'email',
        ]

        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'}
            )
        }