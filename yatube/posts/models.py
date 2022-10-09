from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()
MIN_TEXT_MODEL: int = 20


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Заголовок')
    slug = models.SlugField(unique=True,
                            verbose_name='Параметр')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:MIN_TEXT_MODEL]

    class Meta:
        ordering = ['-pub_date']


class Comment(CreatedModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Пост'
                             )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Введите текст комментария')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
