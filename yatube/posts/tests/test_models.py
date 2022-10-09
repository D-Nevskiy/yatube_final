from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, MIN_TEXT_MODEL

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_help_text(self):
        help_texts = {'text': 'Введите текст поста',
                      'group': 'Выберите группу'}
        for field, value in help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    value)

    def test_label(self):
        verboses = {'text': 'Текст поста',
                    'pub_date': 'Дата публикации',
                    'group': 'Группа',
                    'author': 'Автор'}
        for field, value in verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    value)

    def test_Group_and_Post_models_have_correct(self):
        group = PostModelTest.group
        post = PostModelTest.post
        models = {group.title: str(group),
                  post.text[:MIN_TEXT_MODEL]: str(post)}
        for field, value in models.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)
