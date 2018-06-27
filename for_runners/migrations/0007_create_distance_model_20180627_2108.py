# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-27 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion



def set_distance(apps, schema_editor):

    # FIXME: We need the "real" model, because the code in save() must be executed!
    # GpxModel = apps.get_model('for_runners', 'GpxModel')
    # DistanceModel = apps.get_model('for_runners', 'DistanceModel')
    from for_runners.models import GpxModel
    from for_runners.models import DistanceModel

    DistanceModel.objects.create(distance_km=0.4)
    DistanceModel.objects.create(distance_km=0.8)
    DistanceModel.objects.create(distance_km=5.0)
    DistanceModel.objects.create(distance_km=6.5)
    DistanceModel.objects.create(distance_km=7.5)
    DistanceModel.objects.create(distance_km=8.5)
    DistanceModel.objects.create(distance_km=10.0)
    DistanceModel.objects.create(distance_km=21.0975)
    DistanceModel.objects.create(distance_km=42.195)

    for track in GpxModel.objects.all():
        track.save()
        print(".", end="", flush=True)
    print()



class Migration(migrations.Migration):

    dependencies = [
        ('for_runners', '0006_remove_gpxmodel_map_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistanceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance_km', models.DecimalField(decimal_places=4, help_text='The ideal track length in kilometer.', max_digits=7, unique=True)),
                ('variance', models.PositiveSmallIntegerField(default=5, help_text='Maximum (+/-) deviation in percent to match this distance.')),
                ('min_distance_m', models.PositiveIntegerField(editable=False, blank=True, null=True)),
                ('max_distance_m', models.PositiveIntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Distance',
                'ordering': ('-distance_km',),
                'verbose_name_plural': 'Distances',
            },
        ),
        migrations.AddField(
            model_name='gpxmodel',
            name='ideal_distance',
            field=models.ForeignKey(blank=True, help_text='Length in meters (calculated 3-dimensional used latitude, longitude, and elevation)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tracks', to='for_runners.DistanceModel'),
        ),
        migrations.RunPython(set_distance, reverse_code=migrations.RunPython.noop),
    ]
