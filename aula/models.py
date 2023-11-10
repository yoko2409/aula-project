from django.db import models
from django.urls import reverse
from accounts.models import CustomUser
from django.conf import settings
# Create your models here.
class Course(models.Model):
    title = models.CharField(
        verbose_name='クラス名',
        max_length=200,
    )
    description = models.TextField(
        verbose_name='説明文'
    )
    image = models.ImageField(
        verbose_name='イメージ',
        upload_to='courses',
        blank=True,
        null=True,
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='コース作成者',
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='割り当て生徒',
    )
    created_at = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True,
    )

    def __str__(self):
        return self.title

class Material(models.Model):
    title = models.CharField(
        verbose_name='資料タイトル',
        max_length=200,
    )
    content = models.TextField(
        verbose_name='資料内容',
        blank=True,
        null=True,
    )
    file = models.FileField(
        verbose_name='添付ファイル',
        upload_to='materials/',
        blank=True,
        null=True,
    )
    course_name = models.ForeignKey(
        Course,
        verbose_name='作成したクラス',
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        CustomUser,
        verbose_name='作成者',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('aula:material_detail', kwargs={'pk': self.pk})

class Comment(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    target = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField(
        max_length=50,
    )
    create_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.content

class Note(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    target = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='note',
    )
    content = models.TextField(
        max_length=300,
    )
    create_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=225)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    submitted_file = models.FileField(upload_to='submissions/')
    timestamp = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=3, decimal_places=0, default=0, null=True, blank=True)

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"