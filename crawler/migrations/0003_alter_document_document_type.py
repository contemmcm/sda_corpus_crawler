# Generated by Django 4.2.13 on 2024-06-22 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0002_document_is_review_finished_document_text_revised'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(choices=[('book', 'Book'), ('youtube', 'Youtube Transcript'), ('audio', 'Audio Transcript')], default='book', max_length=30),
        ),
    ]
