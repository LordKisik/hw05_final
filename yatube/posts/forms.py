from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """При создании или редактировании поста в поле группы, при отсутствии
    выбора, содержит сообщение -- Группа не выбрана --"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].empty_label = "-- Группа не выбрана --"

    class Meta:
        model = Post
        labels = {"group": "Группа", "text": "Текст поста"}
        help_texts = {"group": "Выберите группу", "text": "Введите текст"}
        fields = ["group", "text", "image"]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": "Текст комментария"}
        help_texts = {"text": "Введите текст комментария"}
