# Generated by Django 5.0.4 on 2024-06-05 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publico', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='calificacion',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]