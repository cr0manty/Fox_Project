# Generated by Django 2.2.7 on 2020-02-12 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_user_vk_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='vk_login',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='vk_password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
