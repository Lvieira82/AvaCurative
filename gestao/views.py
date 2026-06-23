import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from pacientes.models import Paciente
from consultas.models import Consulta, AgendaConsulta


@login_required
def painel_gestao(request):

    hoje = timezone.localdate()

    total_pacientes = Paciente.objects.count()
    total_consultas = Consulta.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()

    total_consultas_mes = Consulta.objects.filter(
        criada_em__year=hoje.year,
        criada_em__month=hoje.month
    ).count()

    total_agendamentos = AgendaConsulta.objects.filter(
        data__gte=hoje
    ).exclude(
        status="CANCELADA"
    ).count()

    total_canceladas = AgendaConsulta.objects.filter(
        status="CANCELADA"
    ).count()

    consultas_por_mes = (
        Consulta.objects
        .annotate(mes=TruncMonth("criada_em"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )

    meses_labels = []
    meses_valores = []

    for item in consultas_por_mes:
        if item["mes"]:
            meses_labels.append(item["mes"].strftime("%m/%Y"))
            meses_valores.append(item["total"])

    origem_qs = (
        Paciente.objects
        .values("origem")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    origem_labels = []
    origem_valores = []

    for item in origem_qs:
        origem = item["origem"] or "Não informado"
        origem_labels.append(origem)
        origem_valores.append(item["total"])

    ultimos_agendamentos = (
        AgendaConsulta.objects
        .select_related("paciente")
        .order_by("-data", "-hora")[:10]
    )

    return render(
        request,
        "gestao/painel.html",
        {
            "total_pacientes": total_pacientes,
            "total_consultas": total_consultas,
            "usuarios_ativos": usuarios_ativos,

            "total_consultas_mes": total_consultas_mes,
            "total_agendamentos": total_agendamentos,
            "total_canceladas": total_canceladas,

            "meses_labels": json.dumps(meses_labels),
            "meses_valores": json.dumps(meses_valores),

            "origem_labels": json.dumps(origem_labels),
            "origem_valores": json.dumps(origem_valores),

            "ultimos_agendamentos": ultimos_agendamentos,
        }
    )