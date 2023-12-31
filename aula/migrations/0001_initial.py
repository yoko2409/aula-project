# Generated by Django 4.0 on 2023-11-03 16:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='クラス名')),
                ('description', models.TextField(verbose_name='説明文')),
                ('image', models.ImageField(blank=True, null=True, upload_to='courses', verbose_name='イメージ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('students', models.ManyToManyField(related_name='割り当て生徒', to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='コース作成者', to='accounts.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='資料タイトル')),
                ('content', models.TextField(blank=True, null=True, verbose_name='資料内容')),
                ('file', models.FileField(blank=True, null=True, upload_to='materials/', verbose_name='添付ファイル')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aula.course', verbose_name='作成したクラス')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.customuser', verbose_name='作成者')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=50)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='aula.material')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.customuser')),
            ],
        ),
    ]
