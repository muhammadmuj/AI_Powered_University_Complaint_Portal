# Generated by Django 5.1.1 on 2025-06-27 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0002_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='priority',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10),
        ),
    ]
