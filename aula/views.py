from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy, reverse
from .forms import CourseForm, MaterialForm, CommentForm, NoteForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Course, Material, Comment, Note
from django.views import View, generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Create your views here.
class IndexView(ListView):
    template_name = 'index.html'
    queryset = Course.objects.order_by('created_at')

@method_decorator(login_required, name='dispatch')
class CreateCourseView(CreateView):
    form_class = CourseForm
    template_name = 'create_course.html'
    success_url = reverse_lazy('aula:index')

    def form_valid(self, form):
        coursedata = form.save(commit=False)
        coursedata.teacher = self.request.user
        coursedata.save()
        return super().form_valid(form)

# コース作成成功ビュー
class CreateSuccessView(TemplateView):
    template_name = 'create_success.html'

class CourseDetailView(DetailView):
    template_name = 'course_detail.html'
    model = Course

class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'course_delete.html'
    success_url = reverse_lazy('aula:index')

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class MaterialCreateView(CreateView):
    form_class = MaterialForm
    model = Material
    template_name = 'material_create.html'

    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        form.instance.course_name = course
        form.instance.teacher = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        course_id = self.object.course_name.id
        return reverse_lazy('aula:material_list', args=(course_id,))


class MaterialDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Material
    template_name = 'material_delete.html'
    success_url = reverse_lazy('aula:material_done')

    def test_func(self):
        return self.request.user == self.get_object().teacher

    def get_success_url(self):
        course_id = self.object.course_name.id
        return reverse_lazy('aula:material_list', args=(course_id,))

class MaterialDoneView(TemplateView):
    template_name = 'material_done.html'

class MaterialUpdateView(UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'material_update.html'
    # success_url = reverse_lazy('aula:material_updated')

    def get_success_url(self):
        material_id = self.object.id
        return reverse_lazy('aula:material_detail', args=(material_id,))

class MaterialUpdateDoneView(TemplateView):
    template_name = 'material_updated.html'

class MaterialListView(View):

    def get(self, request, course_id):
        materials = Material.objects.filter(course_name=course_id)
        course_obj = Course.objects.get(id=course_id)
        return render(request, 'material_list.html', {'materials': materials, 'course_obj': course_obj})

class MaterialDetailView(DetailView):
    template_name = 'material_detail.html'
    model = Material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm
        context['note_form'] = NoteForm

        return context

class CommentView(LoginRequiredMixin, generic.edit.CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        material_pk = self.kwargs.get('pk')
        material = get_object_or_404(Material, pk=material_pk)

        comment = form.save(commit=False)
        comment.target = material
        comment.save()

        return redirect('aula:material_detail', pk=material_pk)

class NoteView(LoginRequiredMixin, generic.edit.CreateView):
    model = Note
    form_class = NoteForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        material_pk = self.kwargs.get('pk')
        material = get_object_or_404(Material, pk=material_pk)

        note = form.save(commit=False)
        note.target = material
        note.save()

        return redirect('aula:material_detail', pk=material_pk)
