# Generated by Django 3.0.4 on 2020-03-27 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ais', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aiimplementation',
            name='health_endpoint',
        ),
        migrations.RemoveField(
            model_name='aiimplementation',
            name='solution_endpoint',
        ),
        migrations.CreateModel(
            name='AIImplementationEndpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('meta', 'Meta'), ('metrics', 'Metrics')], max_length=30)),
                ('path', models.CharField(max_length=150)),
                ('ai_implementation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endpoints', to='ais.AIImplementation')),
            ],
        ),
        migrations.AddConstraint(
            model_name='aiimplementationendpoint',
            constraint=models.UniqueConstraint(fields=('name', 'ai_implementation'), name='unique_ai_endpoint'),
        ),
    ]