import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestRoutes:
    """Тесты для маршрутов проекта YaNews."""

    def test_home_page_available(self, client):
        """Главная страница доступна анонимному пользователю."""
        url = reverse('news:home')
        response = client.get(url)
        assert response.status_code == 200

    def test_detail_page_available(self, client, news):
        """Страница новости доступна анонимному пользователю."""
        url = reverse('news:detail', args=(news.id,))
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
    def test_comment_pages_available_for_author(self, name, author_client, comment):
        """Страницы редактирования/удаления доступны автору."""
        url = reverse(name, args=(comment.id,))
        response = author_client.get(url)
        assert response.status_code == 200

    @pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
    def test_comment_pages_not_available_for_anonymous(self, name, client, comment):
        """Аноним перенаправляется со страниц редактирования/удаления."""
        url = reverse(name, args=(comment.id,))
        response = client.get(url)
        assert response.status_code == 302
        assert 'login' in response.url

    @pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
    def test_comment_pages_not_available_for_other_user(self, name, not_author_client, comment):
        """Чужой пользователь не может редактировать/удалять комментарий."""
        url = reverse(name, args=(comment.id,))
        response = not_author_client.get(url)
        assert response.status_code == 403

    @pytest.mark.parametrize('name', ['login', 'logout', 'signup'])
    def test_auth_pages_available(self, client, name):
        """Страницы авторизации доступны анонимным пользователям."""
        url = reverse(name)
        response = client.get(url)
        if name in ['logout', 'signup']:
            assert response.status_code in [200, 302, 405]
        else:
            assert response.status_code == 200
