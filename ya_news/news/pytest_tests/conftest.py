import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author():
    """Фикстура автора комментариев."""
    return User.objects.create(username='Автор')


@pytest.fixture
def not_author():
    """Фикстура пользователя, не являющегося автором."""
    return User.objects.create(username='Не автор')


@pytest.fixture
def news():
    """Фикстура новости."""
    return News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, news):
    """Фикстура комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def bulk_news():
    """Фикстура для создания 11 новостей с разными датами."""
    from django.conf import settings
    today = timezone.now().date()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return News.objects.all()


@pytest.fixture
def comment_with_different_dates(news, author):
    """Фикстура для создания комментариев с разными датами."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def author_client(author):
    """Клиент с авторизацией автора."""
    from django.test.client import Client
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Клиент с авторизацией пользователя, не являющегося автором."""
    from django.test.client import Client
    client = Client()
    client.force_login(not_author)
    return client
