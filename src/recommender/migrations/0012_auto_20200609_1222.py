# Generated by Django 3.0.3 on 2020-06-09 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0011_auto_20200609_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='name',
            field=models.CharField(max_length=40, unique=True),
        ),
    ]
