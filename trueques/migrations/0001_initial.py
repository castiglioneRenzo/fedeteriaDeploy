# Generated by Django 5.0.4 on 2024-06-02 15:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('publico', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trueque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateTimeField(auto_now=True)),
                ('fecha_fin', models.DateTimeField(null=True)),
                ('estado', models.CharField(default='Pendiente', max_length=30)),
                ('producto_1', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='producto_1', to='publico.producto')),
                ('producto_2', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='producto_2', to='publico.producto')),
                ('sucursal', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='publico.sucursal')),
            ],
        ),
    ]