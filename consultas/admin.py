from django.contrib import admin
from django.contrib import admin
from .models import Consulta, AuditoriaConsulta, FotoConsulta, AgendaConsulta, Prescricao


@admin.register(AuditoriaConsulta)
class AuditoriaConsultaAdmin(admin.ModelAdmin):
    list_display = (
        "consulta",
        "usuario",
        "editado_em",
    )

    list_filter = (
        "editado_em",
        "usuario",
    )

    search_fields = (
        "consulta__paciente__nome",
        "usuario__username",
    )


admin.site.register(Consulta)
admin.site.register(FotoConsulta)
admin.site.register(AgendaConsulta)
admin.site.register(Prescricao)