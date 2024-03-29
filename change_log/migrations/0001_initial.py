# Generated by Django 3.1.5 on 2021-01-21 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True)),
                ('finished', models.BooleanField()),
                ('comment', models.TextField(max_length=1000)),
                ('headline', models.TextField(max_length=288)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
