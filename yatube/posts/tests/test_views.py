import shutil
import tempfile

from django.db.models.fields.files import ImageFieldFile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        cls.post1 = Post.objects.create(
            author=User.objects.create_user(
                username="admin111",
                password="Admin111admin",
            ),
            text="Тестовый текст 1",
            group=Group.objects.create(
                title="Название 1 группы",
                slug="test-slug1",
                description="Тестовое описание 1 группы",
            ),
            id="1",
            image=uploaded,
        )

        cls.post2 = Post.objects.create(
            author=User.objects.create_user(
                username="admin222",
                password="Admin222admin",
            ),
            text="Тестовый текст 2",
            group=Group.objects.create(
                title="Название 2 группы",
                slug="test-slug2",
                description="Тестовое описание 2 группы",
            ),
            id="2",
            image=uploaded,
        )

        cls.post3 = Post.objects.create(
            author=User.objects.create_user(
                username="admin333",
                password="Admin333admin",
            ),
            text="Тестовый текст 3",
            group=Group.objects.get(
                title="Название 2 группы",
                slug="test-slug2",
                description="Тестовое описание 2 группы",
            ),
            id="3",
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username="lordkisik")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user1 = User.objects.create_user(username="lordkisik111")
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

        self.userpost = User.objects.get(username="admin111")
        self.authorpost_client = Client()
        self.authorpost_client.force_login(self.userpost)

        self.userpost1 = User.objects.get(username="admin222")
        self.authorpost_client1 = Client()
        self.authorpost_client1.force_login(self.userpost1)

    def test_pages_uses_correct_template(self):
        """Тест, проверяющий, что во view-функциях
        используются правильные html-шаблоны"""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_list", kwargs={"slug": "test-slug1"}): (
                "posts/group_list.html"
            ),
            reverse("posts:profile", kwargs={"username": "admin111"}): (
                "posts/profile.html"
            ),
            reverse("posts:post_detail", kwargs={"post_id": "1"}): (
                "posts/post_detail.html"
            ),
            reverse("posts:post_edit", kwargs={"post_id": "1"}): (
                "posts/create_post.html"
            ),
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorpost_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом и списком постов.
        Добавлена проверка на наличие изображения в контексте"""
        response = self.authorized_client.get(reverse("posts:index"))
        # Взяли второй элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым. Также проверили страницу на наличие 3 из 3
        # объектов.
        first_object = response.context["page_obj"][1]
        second_object = response.context["page_obj"][::1]
        cout_object = len(second_object)
        self.assertEqual(first_object.author.username, "admin222")
        self.assertEqual(first_object.text, "Тестовый текст 2")
        self.assertEqual(first_object.group.title, "Название 2 группы")
        self.assertEqual(first_object.id, 2)
        self.assertEqual(cout_object, 3)
        self.assertIsInstance(first_object.image, ImageFieldFile)
        self.assertIn("posts/small", str(first_object.image))

    def test_group_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом и наличием на
        странице постов принадлежащих запрошенной группе. Добавлена проверка на
        наличие изображения в контексте"""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug1"})
        )
        first_object = response.context
        cout_object = len(first_object["page_obj"][::1])
        self.assertEqual(first_object["group"].title, "Название 1 группы")
        self.assertEqual(first_object["group"].slug, "test-slug1")
        self.assertEqual(
            first_object["group"].description, "Тестовое описание 1 группы"
        )
        self.assertEqual(cout_object, 1)
        self.assertIsInstance(
            first_object["page_obj"][-1].image, ImageFieldFile
        )
        self.assertIn("posts/small", str(first_object["page_obj"][-1].image))

    def test_post_another_group(self):
        """Проверка на попадание в другую группу"""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug1"})
        )
        first_object = response.context["page_obj"][0]
        self.assertTrue(first_object.text, "Тестовый текст 2")
        self.assertTrue(first_object.text, "Тестовый текст 3")

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом. Добавлена
        проверка на наличие изображения в контексте"""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "admin222"})
        )
        first_object = response.context["page_obj"][0]
        second_object = response.context["page_obj"][::1]
        cout_object = len(second_object)
        self.assertEqual(response.context["author"].username, "admin222")
        self.assertEqual(first_object.text, "Тестовый текст 2")
        self.assertEqual(cout_object, 1)
        self.assertIsInstance(first_object.image, ImageFieldFile)
        self.assertIn("posts/small", str(first_object.image))

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом. Добавлена
        проверка на наличие изображения в контексте"""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": "1"})
        )
        first_object = response.context["post"]
        self.assertEqual(first_object.text, "Тестовый текст 1")
        self.assertEqual(first_object.group.title, "Название 1 группы")
        self.assertIsInstance(first_object.image, ImageFieldFile)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post для создания поста сформирован с правильным
        контекстом"""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон create_post для редактирования поста сформирован с правильным
        контекстом"""
        response = self.authorpost_client.get(
            reverse("posts:post_edit", kwargs={"post_id": "1"})
        )
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_cache_index(self):
        """Тест кэширования главной страницы"""
        post = Post.objects.get(pk=1)
        response_1 = self.authorized_client.get(reverse("posts:index"))
        post.delete()
        response_2 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(response_1.content, response_3.content)

    def test_add_and_existence_comment(self):
        """Комментировать посты может только авторизованный пользователь.
        Комментарий появляется на странице поста."""
        self.authorpost_client.post(
            f"/posts/{self.post1.id}/comment/",
            {"text": "Тестовый комментарий"},
        )
        response = self.authorpost_client.get(f"/posts/{self.post1.id}/")
        self.assertContains(response, "Тестовый комментарий")
        self.guest_client.post(
            f"/posts/{self.post1.id}/comment/", {"text": "Комментарий гостя"}
        )
        response = self.guest_client.get(f"/posts/{self.post1.id}/")
        self.assertNotContains(response, "Комментарий гостя")

    def test_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок"""
        self.assertEqual(Follow.objects.all().count(), 0)
        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.userpost.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)
        self.authorized_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.userpost.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_appearance_post_on_page_of_the_subscriber(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан"""
        Follow.objects.create(user=self.user, author=self.userpost)
        Follow.objects.create(user=self.user1, author=self.userpost1)
        a = self.authorized_client.get("/follow/").context["page_obj"][0].text
        b = self.authorized_client1.get("/follow/").context["page_obj"][0].text
        self.assertNotEqual(a, b)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        NUMBER_OF_POSTS = 13
        cls.author = User.objects.create_user(
            username="admin111",
            password="Admin111admin",
        )
        cls.group = Group.objects.create(
            title="Тестовый тайтл",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.posts = []
        for number_post in range(NUMBER_OF_POSTS):
            cls.posts.append(
                Post(
                    author=cls.author,
                    text=f"Тестовый текст поста номер {number_post + 1}",
                    group=cls.group,
                    id=number_post + 1,
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username="lordkisik")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        """Шаблоны index, group_list и profile отображают 10 из 13 постов
        на первой странице"""
        list_urls = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "test-slug"}),
            reverse("posts:profile", kwargs={"username": "admin111"}),
        ]
        for tested_url in list_urls:
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get("page_obj").object_list), 10
            )

    def test_second_page_contains_three_posts(self):
        """Шаблоны index, group_list и profile отображают оставшиеся 3 поста
        из 13 на второй странице"""
        list_urls = [
            reverse("posts:index") + "?page=2",
            reverse("posts:group_list", kwargs={"slug": "test-slug"})
            + "?page=2",
            reverse("posts:profile", kwargs={"username": "admin111"})
            + "?page=2",
        ]
        for tested_url in list_urls:
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get("page_obj").object_list), 3
            )
