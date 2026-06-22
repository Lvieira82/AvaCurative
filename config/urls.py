
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from usuarios.views import login_view, logout_view, cadastro_usuario
from pacientes.views import home, cadastrar_paciente, buscar_paciente, arquivo_paciente, autocomplete_pacientes,historico_consultas
from consultas.views import nova_consulta, editar_consulta, prescrever_consulta
from gestao.views import painel_gestao
from gestao.views import painel_gestao, backup_sqlite
from consultas.views import historico_consultas
from consultas.views import (
    nova_consulta,
    editar_consulta,
    agenda,
    novo_agendamento,
    marcar_realizada,
    cancelar_agendamento,
    horarios_disponiveis,
    salvar_agendamento,
    bloquear_horario,
    historico_consultas,
    detalhe_consulta,
    imprimir_consulta,
    prescrever_paciente,
    desbloquear_horario,
    desbloquear_dia,
    desmarcar_consulta_agendada,
    consultar_agendamentos_paciente,

    
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cadastro/', cadastro_usuario, name='cadastro_usuario'),
    path('paciente/novo/', cadastrar_paciente, name='cadastrar_paciente'),
    path('paciente/buscar/', buscar_paciente, name='buscar_paciente'),
    path('paciente/<int:id>/arquivo/', arquivo_paciente, name='arquivo_paciente'),
    path('consulta/nova/<int:paciente_id>/', nova_consulta, name='nova_consulta'),
    path('consulta/editar/<int:id>/', editar_consulta, name='editar_consulta'),
    path('gestao/', painel_gestao, name='painel_gestao'),
    path("gestao/", painel_gestao, name="painel_gestao"),
    path("gestao/backup/", backup_sqlite, name="backup_sqlite"),
    path("agenda/", agenda, name="agenda"),
    path("agenda/novo/", novo_agendamento, name="novo_agendamento"),
    path("agenda/<int:id>/realizada/", marcar_realizada, name="marcar_realizada"),
    path("agenda/<int:id>/cancelar/", cancelar_agendamento, name="cancelar_agendamento"),
    path("pacientes/autocomplete/", autocomplete_pacientes, name="autocomplete_pacientes"),
    path("agenda/", agenda, name="agenda"),
    path("consultas/historico/<int:paciente_id>/", historico_consultas,name="historico_consultas"),
    path("agenda/horarios/", horarios_disponiveis, name="horarios_disponiveis"),
    path("agenda/salvar/", salvar_agendamento, name="salvar_agendamento"),
    path("agenda/bloquear/", bloquear_horario, name="bloquear_horario"),
    path("paciente/<int:id>/historico/", historico_consultas, name="historico_consultas"),
    path("consulta/nova/<int:paciente_id>/", nova_consulta, name="nova_consulta"),
    path("consulta/<int:id>/", detalhe_consulta, name="detalhe_consulta"),
    path("consulta/<int:id>/imprimir/", imprimir_consulta, name="imprimir_consulta"),
    path("consulta/<int:id>/prescrever/", prescrever_consulta, name="prescrever_consulta"),
    path("paciente/<int:id>/prescrever/", prescrever_paciente, name="prescrever_paciente"),
    path("agenda/desbloquear/", desbloquear_horario, name="desbloquear_horario"),
    path("agenda/desbloquear-dia/", desbloquear_dia, name="desbloquear_dia"),
    path("agenda/desmarcar/<int:id>/", desmarcar_consulta_agendada, name="desmarcar_consulta_agendada"),
    path("agenda/consultar-agendados/", consultar_agendamentos_paciente, name="consultar_agendamentos_paciente"),
        
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )