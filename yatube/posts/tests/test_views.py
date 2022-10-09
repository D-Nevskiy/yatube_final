from django import forms
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from ..utils import COUNT_POSTS
from ..models import Post, Group, Follow

TEST_POST = 9
User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.posts = []
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        for i in range(TEST_POST):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=cls.group,
                image=cls.image
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': "test_slug"}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': "testuser"}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': "1"}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': "1"}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_added_correctly(self):
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=self.image)
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'testuser'}))
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index)
        self.assertIn(post, group)
        self.assertIn(post, profile)

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField
        }
        for i, expected in form_fields.items():
            with self.subTest(i=i):
                form_field = response.context.get('form').fields.get(i)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        post_text = {
            response.context['post'].text: 'Тестовый пост',
            response.context['post'].group: 'Тестовая группа',
            response.context['post'].author: 'testuser'
        }
        for i, expected in post_text.items():
            self.assertEqual(post_text[i], expected)

    def test_cache_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='Тестовый текст',
            author=self.user, )
        response_old = self.authorized_client.get(reverse('posts:index'))
        post_old = response_old.content
        self.assertEqual(post_old, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        post_new = response_new.content
        self.assertNotEqual(post_old, post_new)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='testuser2')
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Danya')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        list_urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug2'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'testuser2'}):
                'posts/profile.html',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context.get('page_obj')
                                 .object_list), COUNT_POSTS)

    def test_second_page_contains_three_posts(self):
        list_urls = {
            reverse('posts:index') + '?page=2': 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug2'})
            + '?page=2': 'posts/group_list.html',
            reverse('posts:profile', kwargs={"username": "testuser2"})
            + "?page=2": 'posts/profile.html',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context.get('page_obj')
                                 .object_list), 3)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.user2 = User.objects.create_user(username='testuser2')
        cls.user3 = User.objects.create_user(username='testuser3')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_user_follower_and_unfollower(self):
        follow_count = Follow.objects.filter(user=FollowTest.user).count()
        data_follow = {'user': FollowTest.user,
                       'author': FollowTest.user3}
        url_redirect = reverse(
            'posts:profile',
            kwargs={'username': FollowTest.user3.username})
        response = self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={
                'username': FollowTest.user3.username}),
            data=data_follow, follow=True)
        new_count_follow = Follow.objects.filter(
            user=FollowTest.user).count()
        self.assertTrue(Follow.objects.filter(
            user=FollowTest.user,
            author=FollowTest.user3).exists())
        self.assertRedirects(response, url_redirect)
        self.assertEqual(follow_count + 1, new_count_follow)
        response_unfollow = self.authorized_client.post(
            reverse('posts:profile_unfollow', kwargs={
                'username': FollowTest.user3.username}),
            data=data_follow, follow=True)
        self.assertRedirects(response_unfollow, url_redirect)
        new2_count_follow = Follow.objects.filter(
            user=FollowTest.user).count()
        self.assertEqual(follow_count, new2_count_follow)

    def test_follower_post(self):
        post = Post.objects.create(
            text='Я нахожусь в подписках',
            author=self.user3)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts1 = response.context['page_obj']
        self.assertNotIn(post, posts1)
        Follow.objects.create(user=self.user, author=self.user3)
        response_2 = self.authorized_client.get(reverse('posts:follow_index'))
        posts2 = response_2.context['page_obj']
        self.assertIn(post, posts2)
