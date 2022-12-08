from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            id='1',
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='lordkisik')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create_post_for_guest_client(self):
        """Неавторизованный пользователь не может создать пост"""
        form_data = {
            'group': self.group.id,
            'text': 'Текст в форме создания поста для guest_client'
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)
        self.assertFalse(Post.objects.filter(
            text='Текст в форме создания поста для guest_client'))

    def test_form_create_post_for_authorized_client(self):
        """Авторизованный пользователь может создать пост. После создания поста
        происходит перенаправление на страницу постов пользователя."""
        count_posts = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Текст в форме создания поста для authorized_client'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=('lordkisik',)))
        self.assertEqual(Post.objects.count(), count_posts + 1)

    def test_authorized_form_edit_post(self):
        """Авторизованный пользователь может отредактировать пост.
        После редактирования происходит перенаправление на страницу поста."""
        form_data = {
            'group': self.group.id,
            'text': 'Текст из формы при создании поста'
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        self.authorized_client.get(f'/lordkisik/{post.id}/edit/')
        form_data = {
            'group': self.group.id,
            'text': 'Отредактированный текст из формы'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post.id
                    }),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(post.id,)))
        self.assertEqual(post.text, 'Отредактированный текст из формы')
