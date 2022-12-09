from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200, unique=True, verbose_name="Название группы"
    )
    slug = models.SlugField(max_length=30, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:group_list", kwargs={"slug": self.slug})

    class Meta:
        ordering = ("title",)
        verbose_name = "категорию"
        verbose_name_plural = "Группы"


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста", help_text="Введите текст поста"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="group_list",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    def __str__(self):
        return self.text[:15]

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"post_id": self.pk})

    class Meta:
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"
        verbose_name = "публикацию"
        verbose_name_plural = "Публикации"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        verbose_name = "подписку"
        verbose_name_plural = "Подписки"
