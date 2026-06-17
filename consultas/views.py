from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from pacientes.models import Paciente
from .models import Consulta
from .forms import ConsultaForm
from django.utils import timezone
from .models import AgendaConsulta
from .forms import ConsultaForm
from datetime import time
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from pacientes.models import Paciente
from .models import AgendaConsulta
from .models import Consulta
from datetime import datetime, timedelta
from .models import Consulta, AuditoriaConsulta
from .models import Consulta, AuditoriaConsulta, FotoConsulta
from django.utils import timezone
from django.contrib import messages
from .forms import ConsultaForm, PrescricaoForm


HORARIOS_PADRAO = [
    "08:00", "09:00", "10:00", "11:00", "12:00",
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
]

@login_required
def historico_consultas(request, id):

    paciente = get_object_or_404(
        Paciente,
        id=id
    )

    consultas = (
        Consulta.objects
        .filter(paciente=paciente)
        .order_by("-criada_em")
    )

    hoje = timezone.localtime().date()

    for consulta in consultas:

        data_consulta = timezone.localtime(
            consulta.criada_em
        ).date()

        consulta.pode_editar = data_consulta == hoje

    return render(
        request,
        "consultas/historico.html",
        {
            "paciente": paciente,
            "consultas": consultas,
        }
    )
    
@login_required
def agenda(request):

    pacientes = Paciente.objects.all().order_by("nome")

    return render(
        request,
        "consultas/agenda.html",
        {
            "pacientes": pacientes
        }
    )


@login_required
def horarios_disponiveis(request):

    data = request.GET.get("data")

    ocupados = AgendaConsulta.objects.filter(
        data=data
    ).exclude(
        status="CANCELADA"
    ).values_list(
        "hora",
        flat=True
    )

    ocupados_formatados = [
        h.strftime("%H:%M")
        for h in ocupados
        if h
    ]

    horarios = []

    for h in HORARIOS_PADRAO:

        horarios.append({
            "hora": h,
            "livre": h not in ocupados_formatados
        })

    return JsonResponse(
        {
            "horarios": horarios
        }
    )


@login_required
def salvar_agendamento(request):

    if request.method == "POST":

        paciente_id = request.POST.get("paciente")
        data = request.POST.get("data")
        hora = request.POST.get("hora")
        observacao = request.POST.get("observacao")

        paciente = Paciente.objects.get(id=paciente_id)

        agendamento = AgendaConsulta.objects.create(
            paciente=paciente,
            data=data,
            hora=hora,
            observacao=observacao,
            status="AGENDADA"
        )

        mensagem = f"""
Olá, {paciente.nome}!

Sua consulta foi agendada.

Data: {data}
Hora: {hora}

Ava Curative
Especialista em Feridas e Curativos
"""

        if paciente.email:

            send_mail(
                "Consulta Agendada - Ava Curative",
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [paciente.email],
                fail_silently=True
            )

        return redirect("agenda")




@login_required
def bloquear_horario(request):

    if request.method == "POST":

        tipo = request.POST.get("tipo_bloqueio")
        data_inicio = request.POST.get("data_inicio")
        data_fim = request.POST.get("data_fim")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fim = request.POST.get("hora_fim")
        observacao = request.POST.get("observacao")

        horarios_padrao = [
            "08:00", "09:00", "10:00", "11:00", "12:00",
            "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
        ]

        datas = []

        if tipo == "DIA":

            datas = [data_inicio]

        elif tipo == "PERIODO":

            inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

            atual = inicio

            while atual <= fim:
                datas.append(atual.strftime("%Y-%m-%d"))
                atual += timedelta(days=1)

        elif tipo == "HORARIO":

            datas = [data_inicio]

            horarios_padrao = [
                h for h in horarios_padrao
                if hora_inicio <= h <= hora_fim
            ]

        for data in datas:

            for hora in horarios_padrao:

                AgendaConsulta.objects.get_or_create(
                    data=data,
                    hora=hora,
                    defaults={
                        "status": "BLOQUEADA",
                        "observacao": observacao
                    }
                )

        return redirect("agenda")

@login_required
def nova_consulta(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    if request.method == "POST":

        form = ConsultaForm(
            request.POST,
            request.FILES
        )

        fotos = request.FILES.getlist("fotos")

        if len(fotos) > 6:

            messages.error(
                request,
                "É permitido anexar no máximo 6 fotos."
            )

            return render(
                request,
                "consultas/form_consultas.html",
                {
                    "form": form,
                    "paciente": paciente,
                }
            )

        if form.is_valid():

            consulta = form.save(commit=False)
            consulta.paciente = paciente
            consulta.descricao = consulta.anamnese or ""
            consulta.save()

            for foto in fotos:
                FotoConsulta.objects.create(
                    consulta=consulta,
                    imagem=foto
                )

            return redirect(
                "arquivo_paciente",
                id=paciente.id
            )

    else:

        form = ConsultaForm()

    return render(
        request,
        "consultas/form_consultas.html",
        {
            "form": form,
            "paciente": paciente,
        }
    )

@login_required
def editar_consulta(request, id):

    consulta = get_object_or_404(
        Consulta,
        id=id
    )

    data_consulta = timezone.localtime(
        consulta.criada_em
    ).date()

    hoje = timezone.localtime().date()

    if data_consulta != hoje:

        messages.error(
            request,
            "Esta consulta não pode mais ser editada."
        )

        return redirect(
            "detalhe_consulta",
            id=consulta.id
        )

    if request.method == "POST":

        consulta_antiga = Consulta.objects.get(
            id=consulta.id
        )

        form = ConsultaForm(
            request.POST,
            request.FILES,
            instance=consulta
        )

        fotos_novas = request.FILES.getlist("fotos")

        total_atual = consulta.fotos.count()

        if total_atual + len(fotos_novas) > 6:

            messages.error(
                request,
                "A consulta pode ter no máximo 6 fotos."
            )

            return redirect(
                "editar_consulta",
                id=consulta.id
            )

        if form.is_valid():

            consulta_atualizada = form.save(commit=False)
            consulta_atualizada.descricao = consulta_atualizada.anamnese or ""
            consulta_atualizada.save()

            for foto in fotos_novas:
                FotoConsulta.objects.create(
                    consulta=consulta_atualizada,
                    imagem=foto
                )

            AuditoriaConsulta.objects.create(
                consulta=consulta_atualizada,
                usuario=request.user,

                descricao_anterior=consulta_antiga.descricao,
                descricao_nova=consulta_atualizada.descricao,

                diabetes_anterior=consulta_antiga.diabetes,
                diabetes_novo=consulta_atualizada.diabetes,

                hipertensao_anterior=consulta_antiga.hipertensao,
                hipertensao_novo=consulta_atualizada.hipertensao,

                doenca_cronica_anterior=consulta_antiga.doenca_cronica,
                doenca_cronica_novo=consulta_atualizada.doenca_cronica,
            )

            messages.success(
                request,
                "Consulta atualizada com sucesso."
            )

            return redirect(
                "detalhe_consulta",
                id=consulta_atualizada.id
            )

    else:

        form = ConsultaForm(
            instance=consulta
        )

    return render(
        request,
        "consultas/form_consultas.html",
        {
            "form": form,
            "consulta": consulta,
            "paciente": consulta.paciente,
            "editando": True,
        }
    )
@login_required
def agenda(request):

    hoje = timezone.localdate()

    agendamentos = (
        AgendaConsulta.objects
        .filter(data__gte=hoje)
        .order_by("data", "hora")
    )

    return render(
        request,
        "consultas/agenda.html",
        {
            "agendamentos": agendamentos
        }
    )


@login_required
def novo_agendamento(request):

    if request.method == "POST":

        form = AgendaConsultaForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("agenda")

    else:
        form = AgendaConsultaForm()

    return render(
        request,
        "consultas/form_agendamento.html",
        {
            "form": form
        }
    )


@login_required
def marcar_realizada(request, id):

    agendamento = get_object_or_404(
        AgendaConsulta,
        id=id
    )

    agendamento.status = "REALIZADA"
    agendamento.save()

    return redirect("agenda")


@login_required
def cancelar_agendamento(request, id):

    agendamento = get_object_or_404(
        AgendaConsulta,
        id=id
    )

    agendamento.status = "CANCELADA"
    agendamento.save()

    return redirect("agenda")

@login_required
def detalhe_consulta(request, id):

    consulta = get_object_or_404(
        Consulta,
        id=id
    )

    agora = timezone.localtime()

    fim_do_dia = timezone.localtime(
        consulta.criada_em
    ).replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=0
    )

    pode_editar = agora <= fim_do_dia

    return render(
        request,
        "consultas/detalhe_consulta.html",
        {
            "consulta": consulta,
            "paciente": consulta.paciente,
            "pode_editar": pode_editar,
        }
    )
@login_required
def imprimir_consulta(request, id):

    consulta = get_object_or_404(
        Consulta,
        id=id
    )

    fotos_ids = request.GET.getlist("fotos")

    if fotos_ids:
        fotos = consulta.fotos.filter(
            id__in=fotos_ids
        )[:6]
    else:
        fotos = consulta.fotos.none()

    return render(
        request,
        "consultas/imprimir_consulta.html",
        {
            "consulta": consulta,
            "paciente": consulta.paciente,
            "fotos": fotos,
        }
    )
@login_required
def prescrever_consulta(request, id):

    consulta = get_object_or_404(
        Consulta,
        id=id
    )

    return render(
        request,
        "consultas/prescricao.html",
        {
            "consulta": consulta,
            "paciente": consulta.paciente,
        }
    )
@login_required
def prescrever_paciente(request, id):

    paciente = get_object_or_404(
        Paciente,
        id=id
    )

    if request.method == "POST":

        form = PrescricaoForm(
            request.POST
        )

        if form.is_valid():

            prescricao = form.save(commit=False)
            prescricao.paciente = paciente
            prescricao.save()

            return redirect(
                "arquivo_paciente",
                id=paciente.id
            )

    else:

        form = PrescricaoForm()

    return render(
        request,
        "consultas/prescricao.html",
        {
            "form": form,
            "paciente": paciente,
        }
    )
@login_required
def horarios_disponiveis(request):

    data = request.GET.get("data")

    if not data:
        return JsonResponse({
            "horarios": []
        })

    agendamentos = AgendaConsulta.objects.filter(
        data=data
    ).exclude(
        status="CANCELADA"
    )

    horarios_ocupados = set()

    for agendamento in agendamentos:

        if agendamento.hora:
            horarios_ocupados.add(
                agendamento.hora.strftime("%H:%M")
            )

    horarios = []

    for hora in HORARIOS_PADRAO:

        if hora in horarios_ocupados:
            horarios.append({
                "hora": hora,
                "status": "BLOQUEADO",
                "disponivel": False
            })
        else:
            horarios.append({
                "hora": hora,
                "status": "LIVRE",
                "disponivel": True
            })

    return JsonResponse({
        "horarios": horarios
    })
@login_required
def desbloquear_horario(request):

    data = request.GET.get("data")
    hora = request.GET.get("hora")

    if data and hora:
        AgendaConsulta.objects.filter(
            data=data,
            hora=hora,
            status="BLOQUEADA"
        ).delete()

    return redirect("agenda")
@login_required
def desbloquear_dia(request):

    if request.method == "POST":

        data = request.POST.get("data")

        AgendaConsulta.objects.filter(
            data=data,
            status="BLOQUEADA"
        ).delete()

    return redirect("agenda")