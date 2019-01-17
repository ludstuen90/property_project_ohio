# Generated by Django 2.1.5 on 2019-01-17 01:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('propertyrecords', '0012_auto_20181216_0029'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastScraped',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_of_scrape', models.CharField(max_length=5)),
                ('date_of_scrape', models.DateTimeField()),
                ('associated_county', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='propertyrecords.County')),
            ],
        ),
    ]
