# Generated by Django 5.0.4 on 2024-06-05 21:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publico', '0002_usuario_calificacion'),
        ('trueques', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_vendida', models.IntegerField()),
                ('precio_total', models.FloatField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='publico.producto')),
            ],
        ),
        migrations.AddField(
            model_name='trueque',
            name='venta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='trueques.venta'),
        ),
    ]
