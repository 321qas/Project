# Generated by Django 5.2.1 on 2025-07-09 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_user_dob_user_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', '남자'), ('female', '여자')], max_length=10, null=True),
        ),
    ]
