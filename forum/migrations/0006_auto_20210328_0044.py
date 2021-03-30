# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-28 00:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0005_auto_20210328_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcript',
            name='advisors',
            field=models.ManyToManyField(related_name='invited_transcripts', to='student.Student'),
        ),
        migrations.AlterField(
            model_name='transcript',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_transcripts', to='student.Student'),
        ),
    ]