from django.db import models
from django.db import models
from django.utils import timezone
from pacientes.models import Paciente
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Consulta(models.Model):

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="prescricoes",
        null=True,
        blank=True
    )

    diagnostico_clinico = models.TextField(
        blank=True,
        null=True,
        verbose_name="Diagnóstico Clínico"
    )

    anamnese = models.TextField(
        blank=True,
        null=True
    )

    conduta = models.TextField(
        blank=True,
        null=True
    )

    diabetes = models.BooleanField(
        default=False
    )

    hipertensao = models.BooleanField(
        default=False,
        verbose_name="Hipertenso"
    )

    doenca_cronica = models.BooleanField(
        default=False,
        verbose_name="Doença crônica"
    )
    
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observação / Evolução"
    )

    criada_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizada_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Consulta de {self.paciente.nome}"
    
    def pode_editar(self):

        agora = timezone.localtime()

        criada = timezone.localtime(
            self.criada_em
        )

        return agora.date() == criada.date()

    
class AuditoriaConsulta(models.Model):

    consulta = models.ForeignKey(
        Consulta,
        on_delete=models.CASCADE,
        related_name="auditorias"
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    descricao_anterior = models.TextField(blank=True, null=True)
    descricao_nova = models.TextField(blank=True, null=True)

    diabetes_anterior = models.BooleanField(default=False)
    diabetes_novo = models.BooleanField(default=False)

    hipertensao_anterior = models.BooleanField(default=False)
    hipertensao_novo = models.BooleanField(default=False)

    doenca_cronica_anterior = models.BooleanField(default=False)
    doenca_cronica_novo = models.BooleanField(default=False)

    editado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auditoria da consulta {self.consulta.id}"
class AgendaConsulta(models.Model):

    STATUS_CHOICES = [
        ("AGENDADA", "Agendada"),
        ("REALIZADA", "Realizada"),
        ("CANCELADA", "Cancelada"),
        ("BLOQUEADA", "Bloqueada"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="agendamentos",
        blank=True,
        null=True
    )

    data = models.DateField()

    hora = models.TimeField(
        blank=True,
        null=True
    )

    observacao = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AGENDADA"
    )

    criado_em = models.DateTimeField(auto_now_add=True)

class Meta:
    ordering = ["data", "hora"]
    unique_together = ("data", "hora")
    def __str__(self):
        return f"{self.data} {self.hora} - {self.status}"
    
class FotoConsulta(models.Model):

    consulta = models.ForeignKey(
        Consulta,
        on_delete=models.CASCADE,
        related_name="fotos"
    )

    imagem = models.ImageField(
        upload_to="consultas/fotos/"
    )

    enviada_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Foto da consulta {self.consulta.id}"
class Prescricao(models.Model):

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="prescricoes_paciente",
        null=True,
        blank=True
    )

    consulta = models.ForeignKey(
        Consulta,
        on_delete=models.SET_NULL,
        related_name="prescricoes_consulta",
        null=True,
        blank=True
    )

    texto = models.TextField(
        verbose_name="Prescrição"
    )

    criada_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizada_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        if self.paciente:
            return f"Prescrição {self.id} - {self.paciente.nome}"

        return f"Prescrição {self.id}"