from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("consultas", "0008"),
    ]

    operations = [
        migrations.AddField(
            model_name="consulta",
            name="status",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("RASCUNHO", "Rascunho"),
                    ("DEFINITIVA", "Definitiva"),
                ],
                default="RASCUNHO",
            ),
        ),

        migrations.AddField(
            model_name="consulta",
            name="finalizada_em",
            field=models.DateTimeField(
                null=True,
                blank=True,
            ),
        ),

        migrations.AddField(
            model_name="consulta",
            name="finalizada_por",
            field=models.ForeignKey(
                to="auth.user",
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                related_name="consultas_finalizadas",
            ),
        ),
    ]
