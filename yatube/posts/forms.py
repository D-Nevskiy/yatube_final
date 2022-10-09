from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {'text': 'Тeкст поста', 'group': 'Группа'}
        help_texts = {'text': 'Введите текст поста',
                      'group': 'Выберите группу'}
        fields = ('text', 'group', 'image')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Тeкст комментария'}
        help_texts = {'text': 'Введите текст комментария'}
        fields = ('text',)

