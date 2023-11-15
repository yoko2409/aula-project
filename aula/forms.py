from django.forms import ModelForm
from .models import Course, Material, Comment, Note
from django import forms


class CourseForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'クラス名を入力'}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '説明を入力', 'rows': 5}))
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Course
        fields = ['title', 'description', 'image']


class MaterialForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'タイトルを入力'}))
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '内容を入力', 'rows': 5}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Material
        fields = ['title', 'content', 'file']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'rows': '1', 'cols': '70'})


class NoteForm(ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'メモを入力', 'rows': 5}))

    class Meta:
        model = Note
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'rows': '3', 'cols': '30'})
