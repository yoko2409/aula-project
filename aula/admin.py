from django.contrib import admin
from .models import Course, Material, Comment, Note, Assignment, Submission
# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course_name', 'teacher', 'content', 'created_at')
    list_display_links = ('id', 'title', 'course_name', 'teacher', 'content', 'created_at')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target', 'content', 'create_at')
    list_display_links = ('id', 'user', 'target', 'content', 'create_at')

class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target', 'content', 'create_at')
    list_display_links = ('id', 'user', 'target', 'content', 'create_at')

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    list_display_links = ('id', 'title', 'created_at')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'student', 'submitted_file')
    list_display_links = ('id', 'assignment', 'student', 'submitted_file')


admin.site.register(Course, CourseAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)