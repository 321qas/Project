# Generated by Django 5.2.1 on 2025-07-09 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='count',
            field=models.IntegerField(default=0, help_text='태그가 조회된 횟수'),
        ),
    ]
