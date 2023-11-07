from django.urls import path
from . import views

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
    path('material/note/<int:pk>/', views.NoteView.as_view(), name='material_note'),
]
