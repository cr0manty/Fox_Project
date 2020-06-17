# Generated by Django 2.2.10 on 2020-06-17 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200515_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegrambotlogs',
            name='log_type',
            field=models.IntegerField(choices=[(0, 'Error'), (1, 'Not Sended'), (2, 'Not Found'), (3, 'Success')], default=0),
        ),
    ]
