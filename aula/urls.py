from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'aula'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateCourseView.as_view(), name='create'),
    path('create_done/', views.CreateSuccessView.as_view(), name='create_done'),
    path('create/', views.CreateCourseView.as_view(), name='create'),
    path('course-detail/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:pk>/delete', views.CourseDeleteView.as_view(), name='course_delete'),
    path('materials/<int:course_id>/', views.MaterialListView.as_view(), name='material_list'),
    path('materials/<int:course_id>/create/', views.MaterialCreateView.as_view(), name='material_create'),
    path('material/<int:pk>/', views.MaterialDetailView.as_view(), name='material_detail'),
    path('material/<int:pk>/update', views.MaterialUpdateView.as_view(), name='material_update'),
    path('material/<int:pk>/delete', views.MaterialDeleteView.as_view(), name='material_delete'),
    path('material/updated', views.MaterialUpdateDoneView.as_view(), name='material_updated'),
    path('material/done', views.MaterialDoneView.as_view(), name='material_done'),
    path('material/comment/<int:pk>/', views.CommentView.as_view(), name='material_comment'),
    path('material/note/<int:pk>/', views.NoteCreateView.as_view(), name='material_note'),
    path('material/note/<int:pk>/update/', views.NoteUpdateView.as_view(), name='note_update'),
    path('material/note/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    path('enroll/<int:course_id>', views.course_enroll, name='enroll_course'),
    path('assignments/<int:course_id>/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/<int:course_id>/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignment/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignment/<int:pk>/update', views.AssignmentUpdateView.as_view(), name='assignment_update'),
    path('assignment/<int:pk>/delete', views.AssignmentDeleteView.as_view(), name='assignment_delete'),
    path('assignment/result/<int:pk>/', views.AssignmentResultView.as_view(), name='assignment_result'),
    path('submissions/<int:pk>/create/', views.SubmissionCreateView.as_view(), name='submission_create'),
    path('submissions/<int:pk>/eva/', views.SubmissionEvaView.as_view(), name='submission_evaluation'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
