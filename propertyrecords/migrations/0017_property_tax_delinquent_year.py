# Generated by Django 2.1.5 on 2019-01-19 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propertyrecords', '0016_remove_property_tax_delinquent_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='tax_delinquent_year',
            field=models.IntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]