# Generated by Django 2.2.13 on 2020-08-09 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256)),
                ('start_date', models.DateField(editable=False)),
                ('finish_date', models.DateField()),
                ('description', models.CharField(max_length=512)),
            ],
        ),
    ]
