# Generated by Django 3.0.3 on 2020-06-18 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0014_auto_20200609_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='evaluation',
            name='unique_eval_user2',
        ),
        migrations.AddField(
            model_name='evaluation',
            name='accuracy',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='token',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recommender.Token'),
        ),
        migrations.AddConstraint(
            model_name='evaluation',
            constraint=models.UniqueConstraint(fields=('study', 'reclist', 'user'), name='unique_study_eval'),
        ),
        migrations.AddField(
            model_name='study',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommender.Dataset'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='study',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='recommender.Study'),
            preserve_default=False,
        ),
    ]
