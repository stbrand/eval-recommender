# Generated by Django 3.0.3 on 2020-05-23 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0007_auto_20200523_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='testklasse',
            name='genre1',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='testklasse',
            name='genre2',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='testklasse',
            name='genre3',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='testklasse',
            name='tk_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
