# Generated by Django 2.1.3 on 2018-11-21 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('propertyrecords', '0019_taxdata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='current_market_value',
        ),
        migrations.RemoveField(
            model_name='property',
            name='taxable_value',
        ),
        migrations.RemoveField(
            model_name='property',
            name='year_2017_taxes',
        ),
    ]