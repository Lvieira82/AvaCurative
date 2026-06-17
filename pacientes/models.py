from django.db import models



class Paciente(models.Model):

    ORIGEM_CHOICES = [
        ('REDE_SOCIAL', 'Rede Social'),
        ('SITE', 'Site'),
        ('AMIGOS', 'Amigos'),
        ('OUTROS', 'Outros'),
    ]

    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    data_nascimento = models.DateField()
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES)
    email = models.EmailField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome