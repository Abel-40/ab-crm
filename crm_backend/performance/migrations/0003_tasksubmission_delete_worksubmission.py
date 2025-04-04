# Generated by Django 5.1.6 on 2025-03-26 11:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0002_initial'),
        ('tasks', '0005_alter_subtask_assigned_to'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_time', models.DateTimeField()),
                ('progress', models.TextField()),
                ('status', models.CharField(blank=True, choices=[('On Time', 'On Time'), ('Late', 'Late')], max_length=20)),
                ('system_score', models.IntegerField(default=0)),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='tasks.task')),
            ],
        ),
        migrations.DeleteModel(
            name='WorkSubmission',
        ),
    ]
