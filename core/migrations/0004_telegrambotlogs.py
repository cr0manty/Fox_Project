# Generated by Django 2.2.10 on 2020-05-13 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rqlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramBotLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField(blank=True)),
                ('group', models.BooleanField(default=False)),
                ('log_type', models.IntegerField(choices=[(0, 'Error'), (1, 'Not Sended'), (2, 'Not Found')], default=0)),
                ('content', models.TextField(blank=True, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('language', models.CharField(blank=True, max_length=64, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
