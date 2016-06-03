# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0005_auto_20160530_0130'),
    ]

    operations = [
        migrations.AddField(
            model_name='authenticationfield',
            name='title',
            field=models.CharField(default='N/A', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='authenticationfield',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]