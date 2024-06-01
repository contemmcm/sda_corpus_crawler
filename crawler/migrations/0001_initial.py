# Generated by Django 4.2.13 on 2024-06-01 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(db_index=True, unique=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('text', models.TextField()),
                ('lang', models.CharField(blank=True, db_index=True, max_length=30, null=True)),
                ('document_type', models.CharField(choices=[('book', 'Book'), ('youtube', 'Youtube Transcript')], default='book', max_length=30)),
                ('author_id', models.CharField(max_length=255)),
            ],
        ),
    ]
