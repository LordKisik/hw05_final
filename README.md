<h1 align="center">YaTube - сеть блогеров</h1>

## Описание проекта
Функционал: <br/>
Регистрация пользователей<br/>
Публикация постов c возможностью добавления изображения<br/>
Подписка на избранных авторов<br/>
Позможность комментировать посты посты других авторов<br/>
## Используемые технологии:<br/>
- Django - 2.2.16
- Python 3.7
- HTML/CSS
## Как запустить проект:
1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/LordKisik/hw05_final.git
```
2. Cоздать и активировать виртуальное окружение:
```
python -m venv venv

source venv/scripts/activate
```
3. Установить зависимости используемые в проекте:
```
pip install -r requirements.txt
```
4. Перейти в директорию yatube:
```
cd yatube/
```
5. Выполнить команды:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
6. Перейти по ссылке:
```
http://127.0.0.1:8000
```

**Ссылка на сайт:**<br/>
```
http://mrkisik.pythonanywhere.com/
```

**Автор проекта:**<br/>
**Виталий Никонов** - https://github.com/LordKisik<br/>
