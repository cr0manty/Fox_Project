# Generated by Django 2.2.7 on 2020-02-15 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_log_from_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='RQLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_exception', models.BooleanField(default=False)),
                ('exception_text', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
