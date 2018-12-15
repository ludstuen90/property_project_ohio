# Generated by Django 2.1.3 on 2018-12-15 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('propertyrecords', '0009_property_property_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guarantor', models.CharField(max_length=74)),
                ('guarantee', models.CharField(max_length=74)),
                ('sale_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('conveyance_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('conveyance_number', models.IntegerField(blank=True, null=True)),
                ('transfer_date', models.DateField(blank=True, null=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='propertyrecords.Property')),
            ],
        ),
    ]