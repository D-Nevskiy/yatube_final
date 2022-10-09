from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from ..models import Post, Group, User

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user = User.objects.create_user(username='testuser2')

    def test_public_pages(self):
        url_names = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            'unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, status in url_names.items():
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, status)

    def test_redirect_guest_client(self):
        url_names = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/': f'/auth/login/?next=/posts/'
                                            f'{self.post.id}/edit/'
        }
        for page, value in url_names.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)

    def test_urls_authorized_client(self):
        url_names = {
            '/create/',
            f'/posts/{self.post.id}/edit/'
        }
        for page in url_names:
            response = self.authorized_client.get(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        url_names = {
            '/': 'posts/index.html',
            '/123': 'core/404.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'}
        for adress, template in url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
