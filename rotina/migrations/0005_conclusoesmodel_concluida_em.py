# Generated by Django 5.2 on 2025-05-11 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rotina', '0004_resetsemana'),
    ]

    operations = [
        migrations.AddField(
            model_name='conclusoesmodel',
            name='concluida_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
