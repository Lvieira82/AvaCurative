from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PrescricaoForm
from .models import Consulta, Prescricao


@login_required
def ver_prescricao(request, id):
    """
    Abre a prescrição já gravada da consulta.

    A prescrição mais recente é carregada como instance do ModelForm,
    garantindo que o texto existente no banco apareça novamente na tela.
    Se o usuário salvar alterações, a mesma prescrição é atualizada,
    em vez de criar outra prescrição vazia/duplicada.
    """

    consulta = get_object_or_404(
        Consulta,
        id=id
    )

    paciente = consulta.paciente

    prescricao = (
        Prescricao.objects
        .filter(consulta=consulta)
        .order_by("-criada_em", "-id")
        .first()
    )

    if not prescricao:
        return redirect(
            "prescrever_consulta",
            id=consulta.id
        )

    if request.method == "POST":
        form = PrescricaoForm(
            request.POST,
            instance=prescricao
        )

        if form.is_valid():
            form.save()

            return redirect(
                "ver_prescricao",
                id=consulta.id
            )

    else:
        form = PrescricaoForm(
            instance=prescricao
        )

    return render(
        request,
        "consultas/prescricao.html",
        {
            "form": form,
            "consulta": consulta,
            "paciente": paciente,
            "prescricao": prescricao,
        }
    )
