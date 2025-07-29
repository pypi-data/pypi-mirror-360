from django.db import migrations, models
import django.db.models.deletion
import huscy.project_consents.models
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0003_project_project_manager_and_more'),
        ('subjects', '0001_squashed_0009_delete_contactold'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectConsent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_fragments', models.JSONField(verbose_name='Text fragments')),
                ('version', models.PositiveSmallIntegerField(default=1, editable=False, verbose_name='Version')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='projects.project', verbose_name='Project')),
            ],
            options={
                'verbose_name': 'Project consent',
                'verbose_name_plural': 'Project consents',
            },
        ),
        migrations.CreateModel(
            name='ProjectConsentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('template_text_fragments', models.JSONField(verbose_name='Template text fragments')),
            ],
            options={
                'verbose_name': 'Project consent category',
                'verbose_name_plural': 'Project consent categories',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ProjectIntermediary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, default='', max_length=254, verbose_name='Email')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone')),
                ('project_membership', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='projects.membership', verbose_name='Project membership')),
            ],
            options={
                'verbose_name': 'Project intermediary',
                'verbose_name_plural': 'Project intermediaries',
            },
        ),
        migrations.CreateModel(
            name='ProjectConsentToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('created_by', models.CharField(editable=False, max_length=255, verbose_name='Created by')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project', verbose_name='Project')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject')),
            ],
            options={
                'verbose_name': 'Project consent token',
                'verbose_name_plural': 'Project consent tokens',
            },
        ),
        migrations.CreateModel(
            name='ProjectConsentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_consent_version', models.PositiveIntegerField(editable=False, verbose_name='Project consent version')),
                ('filehandle', models.FileField(upload_to=huscy.project_consents.models.ProjectConsentFile.get_upload_path, verbose_name='Filehandle')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('project_consent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_consents.projectconsent', verbose_name='Project consent')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject')),
            ],
            options={
                'verbose_name': 'Project consent file',
                'verbose_name_plural': 'Project consent files',
                'unique_together': {('project_consent', 'project_consent_version', 'subject')},
            },
        ),
    ]
