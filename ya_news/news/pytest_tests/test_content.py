import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
class TestContent:
    """Тесты для контента проекта YaNews."""

    def test_news_count(self, client, bulk_news):
        """Количество новостей на главной — не более 10."""
        url = reverse('news:home')
        response = client.get(url)
        object_list = response.context['object_list']
        news_count = len(object_list)
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client, bulk_news):
        """Новости отсортированы от свежих к старым."""
        url = reverse('news:home')
        response = client.get(url)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates

    def test_comments_order(self, client, news, comment_with_different_dates):
        """Комментарии отсортированы от старых к новым."""
        url = reverse('news:detail', args=(news.id,))
        response = client.get(url)
        assert 'news' in response.context
        news_from_context = response.context['news']
        all_comments = news_from_context.comments.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(self, client, news):
        """Анонимному пользователю форма недоступна."""
        url = reverse('news:detail', args=(news.id,))
        response = client.get(url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, author_client, news):
        """Авторизованному пользователю форма доступна."""
        url = reverse('news:detail', args=(news.id,))
        response = author_client.get(url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
