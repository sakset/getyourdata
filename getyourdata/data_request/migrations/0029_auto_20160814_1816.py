# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-14 18:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_request', '0028_auto_20160812_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackmessagecontent',
            name='pdf_copy',
            field=models.TextField(blank=True, default='A copy of the PDF has been included.', help_text='Included if user requested a copy of his mail request PDF'),
        ),
        migrations.AlterField(
            model_name='feedbackmessagecontent',
            name='pdf_copy_en',
            field=models.TextField(blank=True, default='A copy of the PDF has been included.', help_text='Included if user requested a copy of his mail request PDF', null=True),
        ),
        migrations.AlterField(
            model_name='feedbackmessagecontent',
            name='pdf_copy_fi',
            field=models.TextField(blank=True, default='A copy of the PDF has been included.', help_text='Included if user requested a copy of his mail request PDF', null=True),
        ),
    ]
