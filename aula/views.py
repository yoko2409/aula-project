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
from django.http import HttpResponseRedirect
from itertools import chain
from operator import attrgetter
from django.forms import formset_factory
from django.forms import BaseFormSet


class BaseAnswerFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


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


class CourseItemView(DetailView):
    model = Course
    template_name = 'course_item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materials = Material.objects.filter(course_name=self.object)
        assignments = Assignment.objects.filter(course=self.object)
        questions = Question.objects.filter(material__course_name=self.object)

        # 結合して並び替え
        combined_list = sorted(
            chain(materials, assignments, questions),
            key=attrgetter('created_at'),
            reverse=True
        )

        context['combined_list'] = combined_list

        now = timezone.now()
        current_user = self.request.user
        is_teacher = current_user.role == 'TEACHER'

        for item in context['combined_list']:
            if hasattr(item, 'due_date'):  # Assignmentオブジェクトをチェック
                submission = Submission.objects.filter(
                    assignment=item,
                    student=current_user
                ).order_by('-timestamp').first()  # 最新の提出を取得

                if submission:
                    if submission.status == 'graded':
                        # 評価済みの場合、通常の表示
                        item.display_type = 'normal'
                    elif submission.status == 'resubmission_requested':
                        # 再提出要求の場合、特別な表示
                        item.display_type = 'resubmit'
                    else:
                        # 提出済みの場合、通常の表示
                        item.display_type = 'normal'
                else:
                    if item.due_date < now:
                        # 未提出で期限切れの場合、特別な表示
                        item.display_type = 'overdue'
                    else:
                        # それ以外の場合、通常の表示
                        item.display_type = 'normal'

                # 教師の場合、常に通常の表示
                if is_teacher:
                    item.display_type = 'normal'

        return context


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
        # `created_at`で降順に並べ替える
        materials = Material.objects.filter(course_name=course_id).order_by('-created_at')
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
        # `created_at`で降順に並べ替える
        return Assignment.objects.filter(course=course).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(AssignmentListView, self).get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        context['course_obj'] = get_object_or_404(Course, id=course_id)
        context['now'] = timezone.now()
        user = self.request.user
        context['is_teacher'] = user.role == 'TEACHER'  # または適切なロジックを使用して教師を判断

        # この部分を修正
        if not context['is_teacher']:
            assignments = context['assignments']
            user = self.request.user
            for assignment in assignments:
                submissions = Submission.objects.filter(assignment=assignment, student=user)
                assignment.submitted = submissions.exists()
                if assignment.submitted:
                    latest_submission = submissions.latest('timestamp')
                    assignment.resubmission_requested = latest_submission.status == 'resubmission_requested'
                else:
                    assignment.resubmission_requested = False

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
        submissions = Submission.objects.filter(assignment=self.object)
        user_last_submission = submissions.filter(student=self.request.user).order_by('-timestamp').first()
        context['user_last_submission'] = user_last_submission
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

    def form_valid(self, form):
        # フォームが有効な場合、先に基本のロジックを実行
        response = super().form_valid(form)

        # 評価が完了したので、提出物のステータスを更新
        submission = self.object
        submission.status = 'graded'  # ここで設定したいステータスに変更
        submission.save()

        return response

    def get_success_url(self):
        assignment_id = self.object.assignment.id
        return reverse_lazy('aula:assignment_result', args=(assignment_id,))


class RequestResubmissionView(LoginRequiredMixin, View):
    def post(self, request, submission_id):
        submission = get_object_or_404(Submission, id=submission_id)
        submission.status = 'resubmission_requested'
        submission.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
        questions = Material.objects.filter(role='question').order_by('-created_at')
        course_obj = Course.objects.get(id=course_id)
        return render(request, 'questions/question_list.html', {'materials': questions, 'course_obj': course_obj})


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
    template_name = 'questions/question_answer.html'

    def get(self, request, pk):
        material = Material.objects.get(pk=pk)
        questions = material.questions.all().prefetch_related('choices')  # 選択肢も取得
        form = AnswerForm(questions=questions)
        return render(request, self.template_name, {
            'material': material,
            'form': form,
            'questions_with_choices': [
                (question, question.choices.all()) for question in questions
            ]
        })
    def post(self, request, pk):
        material = Material.objects.get(pk=pk)
        questions = material.questions.all()
        form = AnswerForm(request.POST, questions=questions)

        if form.is_valid():
            # フォームが有効ならばデータを保存
            for question in questions:
                answer = Answer.objects.create(
                    question=question,
                    user=request.user,
                    selected_choice=form.cleaned_data[f'selected_choice_{question.id}']
                )
            return redirect('aula:question_material_detail', pk=pk)  # 成功時のリダイレクト先を指定

        return render(request, self.template_name, {'material': material, 'form': form})


def question_choice_create_view(request, pk):
    material = get_object_or_404(Material, pk=pk)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST, prefix='choice')
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.material = material
            question.save()

            # Save each choice form in the formset as a separate record
            for choice_form in formset:
                if not choice_form.cleaned_data.get('DELETE', False):
                    choice = choice_form.save(commit=False)
                    choice.question = question
                    choice.save()
            return redirect('aula:question_material_detail', pk=pk)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet(prefix='choice')
    return render(request, 'questions/choice_create.html', {'form': form, 'formset': formset})
