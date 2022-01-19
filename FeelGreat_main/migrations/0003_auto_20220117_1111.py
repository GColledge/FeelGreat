# Generated by Django 3.1.7 on 2022-01-17 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FeelGreat_main', '0002_auto_20220117_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='prof_image',
            field=models.ImageField(default=None, null=True, upload_to='prof_pics/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_name',
            field=models.CharField(max_length=150),
        ),
    ]
