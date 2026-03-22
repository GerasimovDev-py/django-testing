from datetime import date, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def pk_from_news(news):
    return (news.pk,)


@pytest.fixture
def pk_from_news_in_list(news):
    return (news.pk,)


@pytest.fixture
def pk_from_comment(comment):
    return (comment.pk,)


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(pk_from_news):
    return reverse('news:detail', args=pk_from_news)


@pytest.fixture
def edit_url(pk_from_comment):
    return reverse('news:edit', args=pk_from_comment)


@pytest.fixture
def delete_url(pk_from_comment):
    return reverse('news:delete', args=pk_from_comment)


@pytest.fixture
def bulk_news(db):
    """Создает список новостей с разными датами для теста пагинации и веса."""
    today = date.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment_with_different_dates(author, news):
    """Создает комментарии с разным временем создания."""
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment
