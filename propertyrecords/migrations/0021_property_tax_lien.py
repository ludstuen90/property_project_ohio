# Generated by Django 2.1.7 on 2019-03-23 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propertyrecords', '0020_auto_20190323_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='tax_lien',
            field=models.BooleanField(default=False),
        ),
    ]
