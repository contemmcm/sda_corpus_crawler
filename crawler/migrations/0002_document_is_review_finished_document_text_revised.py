# Generated by Django 4.2.13 on 2024-06-02 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_review_finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='document',
            name='text_revised',
            field=models.TextField(blank=True, null=True),
        ),
    ]
