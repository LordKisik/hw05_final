from http import HTTPStatus
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='admin111',
                                            password='Admin111admin'),
            text='Тестовая запись для создания нового поста',
            id='1')

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test_slug',
            description='Описание тестовой группы'
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='lordkisk')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.userpost = User.objects.get(username='admin111')
        self.authorpost_client = Client()
        self.authorpost_client.force_login(self.userpost)

    def test_home_group_profile_post_guest_client(self):
        """Cтраницы: главная, посты группы, посты пользователя и
        информация о посте доступны неавторизованному пользователю"""
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/admin111/',
            '/posts/1/',
        )
        for link in url_names:
            with self.subTest():
                response = self.guest_client.get(link)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_and_edit_post_for_guest_client(self):
        """Страницы по адресу /create/ и /posts/id/edit/ перенаправят
        анонимного пользователя на страницу логина"""
        response_url_names = {
            '/create/': "?next=/create/",
            '/posts/1/edit/': "?next=/posts/1/edit/",
        }
        for start, jump in response_url_names.items():
            with self.subTest():
                response = self.guest_client.get(start)
                url = urljoin(reverse('login'), jump)
                self.assertRedirects(response, url)

    def test_home_group_profile_post_createpost_for_authorized_client(self):
        """Cтраницы: главная, посты группы, посты пользователя, информация
        о посте и создание поста доступны авторизованному пользователю"""
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/admin111/',
            '/posts/1/',
            '/create/',
        )
        for link in url_names:
            with self.subTest():
                response = self.authorized_client.get(link)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_for_authorized_client(self):
        """Страница редактирования поста не доступна авторизованному
        пользователю не являющимся автором поста"""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_home_group_profile_post_create_edit_for_authorpost_client(self):
        """Cтраницы: главная, посты группы, посты пользователя, информация
        о посте, создание поста и редактирование поста доступны
        авторизованному пользователю"""
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/admin111/',
            '/posts/1/',
            '/create/',
            '/posts/1/edit/'
        )
        for link in url_names:
            with self.subTest():
                response = self.authorpost_client.get(link)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_for_autour_post(self):
        """Страница редактирования поста доступна автору поста"""
        response = self.authorpost_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/admin111/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in url_names.items():
            with self.subTest(address=address):
                response = self.authorpost_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404_for_guest_client_and_authorized_client(self):
        """"404 ошибка при запросе несуществующей страницы"""
        guest_and_authorized = {
            self.guest_client: '/unexisting_page/',
            self.authorized_client: '/unexisting_page/',
            self.authorpost_client: '/unexisting_page/',
        }
        for user, page in guest_and_authorized.items():
            with self.subTest(page=page):
                response = user.get(page)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
