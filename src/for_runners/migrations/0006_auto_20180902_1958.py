# Generated by Django 2.1.1 on 2018-09-02 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("for_runners", "0005_auto_20180731_1855")]

    operations = [
        migrations.AlterField(
            model_name="gpxmodel",
            name="participation",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="track",
                to="for_runners.ParticipationModel",
            ),
        )
    ]