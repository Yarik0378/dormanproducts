# Generated by Django 3.1.7 on 2021-03-28 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dormanscraper', '0005_auto_20210328_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='finished_codes',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]