import os
import shutil
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import FileResponse
from django.shortcuts import render

from pacientes.models import Paciente
from consultas.models import Consulta


def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador").exists()


@login_required
def painel_gestao(request):

    total_pacientes = Paciente.objects.count()
    total_consultas = Consulta.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()

    pacientes_por_mes = (
        Paciente.objects
        .extra(select={"mes": "strftime('%%m/%%Y', criado_em)"})
        .values("mes")
        .order_by("mes")
    )

    consultas_por_mes = (
        Consulta.objects
        .extra(select={"mes": "strftime('%%m/%%Y', criada_em)"})
        .values("mes")
        .order_by("mes")
    )

    return render(
        request,
        "gestao/painel.html",
        {
            "total_pacientes": total_pacientes,
            "total_consultas": total_consultas,
            "usuarios_ativos": usuarios_ativos,
        }
    )


@login_required
@user_passes_test(is_admin)
def backup_sqlite(request):

    banco = settings.BASE_DIR / "db.sqlite3"

    nome_backup = f"backup_ava_curative_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"

    pasta_backup = settings.BASE_DIR / "backups"

    os.makedirs(pasta_backup, exist_ok=True)

    destino = pasta_backup / nome_backup

    shutil.copy(banco, destino)

    return FileResponse(
        open(destino, "rb"),
        as_attachment=True,
        filename=nome_backup
    )