from django.contrib import admin
from .models import Course, Material, Comment, Note
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

admin.site.register(Course, CourseAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Note, NoteAdmin)