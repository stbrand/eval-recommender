# Generated by Django 3.0.3 on 2020-07-11 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0025_auto_20200702_2009'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crossvalidations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rmse', models.DecimalField(decimal_places=10, max_digits=12, null=True)),
                ('mae', models.DecimalField(decimal_places=10, max_digits=12, null=True)),
                ('fit_time', models.DecimalField(decimal_places=4, max_digits=20, null=True)),
                ('test_time', models.DecimalField(decimal_places=4, max_digits=20, null=True)),
                ('algorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommender.Algorithm')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommender.Dataset')),
            ],
        ),
    ]
