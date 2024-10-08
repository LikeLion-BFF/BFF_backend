# Generated by Django 4.2.15 on 2024-09-15 10:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bingo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('size', models.IntegerField()),
                ('end_date', models.DateTimeField()),
                ('team_count', models.IntegerField()),
                ('winner_bingo_count', models.IntegerField()),
                ('enter_code', models.CharField(max_length=10)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=100)),
                ('bingo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.bingo')),
            ],
        ),
        migrations.CreateModel(
            name='User_Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('bingo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.bingo')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BingoCell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.IntegerField()),
                ('col', models.IntegerField()),
                ('content', models.CharField(max_length=100)),
                ('is_completed_yn', models.BooleanField(default=False)),
                ('completed_photo', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('completed_text', models.TextField(blank=True)),
                ('bingo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.bingo')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.team')),
            ],
        ),
        migrations.AddConstraint(
            model_name='user_team',
            constraint=models.UniqueConstraint(fields=('user', 'team'), name='unique_user_team'),
        ),
    ]
