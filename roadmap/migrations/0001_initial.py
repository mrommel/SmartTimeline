# Generated by Django 3.0.4 on 2020-05-12 10:06

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('desc', models.CharField(max_length=512)),
                ('start_date', models.DateField(verbose_name='date started')),
                ('end_date', models.DateField(verbose_name='date ended')),
            ],
        ),
        migrations.CreateModel(
            name='Lane',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('color', colorfield.fields.ColorField(default='#000000', max_length=18)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roadmap.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('start_date', models.DateField(verbose_name='date started')),
                ('end_date', models.DateField(verbose_name='date ended')),
                ('lane', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roadmap.Lane')),
            ],
        ),
    ]