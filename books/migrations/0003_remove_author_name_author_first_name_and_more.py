# Generated by Django 4.2.2 on 2023-06-15 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_books_isbn_alter_author_salutation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='name',
        ),
        migrations.AddField(
            model_name='author',
            name='first_name',
            field=models.CharField(default='name', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='author',
            name='last_name',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]