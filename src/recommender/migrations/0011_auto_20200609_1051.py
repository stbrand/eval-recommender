# Generated by Django 3.0.3 on 2020-06-09 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0010_auto_20200524_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('valid', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='dataset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recommender.Dataset'),
        ),
        migrations.AlterField(
            model_name='user',
            name='token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recommender.Token'),
        ),
    ]
