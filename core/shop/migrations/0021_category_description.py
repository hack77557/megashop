# Generated by Django 4.2.10 on 2025-02-27 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_product_product_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Опис категорії'),
        ),
    ]
