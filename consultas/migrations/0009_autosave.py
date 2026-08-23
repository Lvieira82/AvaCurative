from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # TROQUE "000X" pelo número da última migration existente
        # do app consultas.
        ("consultas", "000X"),
    ]

    operations = [
        migrations.AddField(
            model_name="consulta",
            name="status",
            field=models.CharField(
                choices=[
                    ("RASCUNHO", "Rascunho"),
                    ("DEFINITIVA", "Definitiva"),
                ],
                default="RASCUNHO",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="consulta",
            name="finalizada_em",
            field=models.DateTimeField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="consulta",
            name="finalizada_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="consultas_finalizadas",
                to="auth.user",
            ),
        ),
    ]
]
