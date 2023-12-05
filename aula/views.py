from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView
from django.views.generic.edit import UpdateView, FormView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from .forms import CourseForm, CourseEnrollForm, MaterialForm, CommentForm, NoteForm, AssignmentForm, SubmissionForm, \
    SubmissionEvaForm, AnswerForm, ChoiceForm, QuestionForm, ChoiceFormSet
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Course, Material, Comment, Note, Assignment, Submission, Question, Choice, Answer
from django.views import View, generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Create your views here.
class IndexView(ListView):
    model = Course
    template_name = 'index.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            if user.role == user.TEACHER:
                return Course.objects.filter(teacher=user).order_by('created_at')
            else:
                return Course.objects.filter(students=user).order_by('created_at')


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


def course_enroll(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseEnrollForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('aula:index')
    else:
        form = CourseEnrollForm(instance=course)
    return render(request, 'course_enroll.html', {'form': form, 'course': course})


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
        form.instance.role = 'material'

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


class MaterialUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'material_update.html'

    # success_url = reverse_lazy('aula:material_updated')

    def test_func(self):
        return self.request.user == self.get_object().teacher


    def get_success_url(self):
        material_id = self.object.id
        material = get_object_or_404(Material, pk=material_id)

        if material.role == 'material':
            return reverse_lazy('aula:material_detail', args=(material_id,))
        elif material.role == 'question':
            return reverse_lazy('aula:question_material_detail', args=(material_id,))


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

        if material.role == 'material':
            return redirect('aula:material_detail', pk=material_pk)
        elif material.role == 'question':
            return redirect('aula:question_material_detail', pk=material_pk)


class NoteCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Note
    form_class = NoteForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        material_pk = self.kwargs.get('pk')
        material = get_object_or_404(Material, pk=material_pk)

        note = form.save(commit=False)
        note.target = material
        note.save()

        if material.role == 'material':
            return redirect('aula:material_detail', pk=material_pk)
        elif material.role == 'question':
            return redirect('aula:question_material_detail', pk=material_pk)


class NoteUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'note_update.html'

    def get_success_url(self):
        material_pk = self.object.target.pk
        material = get_object_or_404(Material, pk=material_pk)

        if material.role == 'material':
            return reverse_lazy('aula:material_detail', kwargs={'pk': material_pk})
        elif material.role == 'question':
            return reverse_lazy('aula:question_material_detail', kwargs={'pk': material_pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(NoteUpdateView, self).form_valid(form)


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'note_delete.html'

    def get_success_url(self):
        material_pk = self.object.target.pk
        material = get_object_or_404(Material, pk=material_pk)

        if material.role == 'material':
            return reverse_lazy('aula:material_detail', kwargs={'pk': material_pk})
        elif material.role == 'question':
            return reverse_lazy('aula:question_material_detail', kwargs={'pk': material_pk})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(NoteDeleteView, self).delete(request, *args, **kwargs)

class AssignmentListView(ListView):
    model = Assignment
    template_name = 'assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        return Assignment.objects.filter(course=course)

    def get_context_data(self, **kwargs):
        context = super(AssignmentListView, self).get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        context['course_obj'] = get_object_or_404(Course, id=course_id)
        context['now'] = timezone.now()  # 現在の日付と時刻を追加
        return context


class AssignmentCreateView(CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignment_create.html'

    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        form.instance.course = course
        form.instance.teacher = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        course_id = self.object.course.id
        return reverse_lazy('aula:assignment_list', args=(course_id,))


class AssignmentDetailView(DetailView):
    model = Assignment
    template_name = 'assignment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submissions'] = Submission.objects.filter(assignment=self.object)
        return context


class AssignmentResultView(DetailView):
    model = Assignment
    template_name = 'assignment_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submissions'] = Submission.objects.filter(assignment=self.object)
        return context


class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignment_update.html'

    def get_success_url(self):
        assignment_id = self.object.id
        return reverse_lazy('aula:assignment_detail', args=(assignment_id,))


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment
    template_name = 'assignment_delete.html'

    def get_success_url(self):
        course_id = self.object.course.id
        return reverse_lazy('aula:assignment_list', args=(course_id,))


class SubmissionCreateView(CreateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'submission_create.html'
    success_url = reverse_lazy('aula:index')

    def form_valid(self, form):
        assignment_id = self.kwargs.get('pk')
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        form.instance.assignment = assignment
        form.instance.student = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        assignment_id = self.object.assignment.id
        return reverse_lazy('aula:assignment_detail', args=(assignment_id,))


class SubmissionEvaView(LoginRequiredMixin, UpdateView):
    model = Submission
    form_class = SubmissionEvaForm
    template_name = 'submission_eva.html'

    def get_success_url(self):
        assignment_id = self.object.assignment.id
        return reverse_lazy('aula:assignment_result', args=(assignment_id,))


@method_decorator(login_required, name='dispatch')
class QuestionMaterialCreateView(CreateView):
    form_class = MaterialForm
    model = Material
    template_name = 'material_create.html'

    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        form.instance.course_name = course
        form.instance.teacher = self.request.user
        form.instance.role = 'question'

        return super().form_valid(form)

    def get_success_url(self):
        course_id = self.object.course_name.id
        return reverse_lazy('aula:material_list', args=(course_id,))

class QuestionMaterialDetail(LoginRequiredMixin, DetailView):
    template_name = 'questions/question_material_detail.html'
    model = Material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm
        context['note_form'] = NoteForm

        material = self.get_object()
        context['questions'] = Question.objects.filter(material=material)

        return context

class QuestionCreateView(UserPassesTestMixin, CreateView):
    model = Question
    fields = ['title', 'description']
    template_name = 'questions/question_create.html'

    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        form.instance.course = course
        form.instance.teacher = self.request.user

        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_teacher()

    def get_success_url(self):
        return reverse_lazy('aula:question_detail', kwargs={'pk': self.object.pk})


class QuestionDetailView(LoginRequiredMixin, DetailView):
    model = Question
    template_name = 'questions/question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choices'] = self.object.choices.all()
        return context

@method_decorator(login_required, name='dispatch')
class QuestionMaterialCreateView(CreateView):
    form_class = MaterialForm
    model = Material
    template_name = 'material_create.html'

    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        form.instance.course_name = course
        form.instance.teacher = self.request.user
        form.instance.role = 'question'

        return super().form_valid(form)

    def get_success_url(self):
        course_id = self.object.course_name.id
        return reverse_lazy('aula:question_list', args=(course_id,))

class QuestionListView(LoginRequiredMixin, View):

    def get(self, request, course_id):
        materials = Material.objects.filter(course_name=course_id)
        course_obj = Course.objects.get(id=course_id)
        return render(request, 'questions/question_list.html', {'materials': materials, 'course_obj': course_obj})


class ChoiceCreateView(LoginRequiredMixin, CreateView):
    model = Choice
    form_class = ChoiceForm
    template_name = 'questions/choice_create.html'

    def get_success_url(self):
        return reverse_lazy('aula:question_detail', kwargs={'pk': self.object.question.pk})

    def form_valid(self, form):
        question_id = self.kwargs.get('pk')
        question = get_object_or_404(Question, pk=question_id)
        form.instance.question = question

        return super().form_valid(form)


class AnswerQuestionView(View):
    def get(self, request, pk):
        material = get_object_or_404(Material, pk=pk)
        questions = material.questions.all()
        forms = {question.id: AnswerForm(question=question) for question in questions}
        return render(request, 'questions/question_answer.html', {'forms': forms, 'questions': questions})

    def post(self, request, pk):
        material = get_object_or_404(Material, pk=pk)
        questions = material.questions.all()
        answers = []
        for question in questions:
            form = AnswerForm(request.POST, question=question)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = question
                answer.user = request.user
                # フォームデータから選択された選択肢を取得
                choice_field_name = f'selected_choice_{question.id}'
                answer.selected_choice = form.cleaned_data[choice_field_name]
                answers.append(answer)

        # すべてのフォームが有効であれば回答を保存
        if len(answers) == len(questions):
            for answer in answers:
                answer.save()
            return redirect('aula:question_material_detail', pk=material.pk)

        # フォームの再表示
        forms = {question.id: AnswerForm(question=question) for question in questions}
        return render(request, 'questions/question_answer.html', {'forms': forms, 'questions': questions})

def question_choice_create_view(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.material = material
            question.save()
            formset.instance = question
            formset.save()
            return redirect('aula:question_material_detail', pk=pk)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()

    return render(request, 'questions/choice_create.html', {'form': form, 'formset': formset})
