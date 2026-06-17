from django import forms
from .models import Consulta, AgendaConsulta, Prescricao

class ConsultaForm(forms.ModelForm):

    class Meta:
        model = Consulta

        fields = [
            "diagnostico_clinico",
            "anamnese",
            "conduta",
            "diabetes",
            "hipertensao",
            "doenca_cronica",
        ]

        widgets = {
            "diagnostico_clinico": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Digite o diagnóstico clínico..."
                }
            ),
            "anamnese": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": "Digite a anamnese..."
                }
            ),
            "conduta": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": "Digite a conduta..."
                }
            ),
        }
class PrescricaoForm(forms.ModelForm):

    class Meta:
        model = Prescricao

        fields = ["texto"]

        widgets = {
            "texto": forms.Textarea(
                attrs={
                    "rows": 20,
                    "class": "form-control"
                }
            )
        }
