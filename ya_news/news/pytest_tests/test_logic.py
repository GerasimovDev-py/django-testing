import pytest
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS


@pytest.mark.django_db
class TestLogic:

    def test_anonymous_user_cant_send_comment(self, client, news):
        url = reverse('news:detail', args=(news.id,))
        comments_before = Comment.objects.count()
        form_data = {'text': 'Текст комментария'}
        response = client.post(url, data=form_data)
        login_url = reverse('login')
        redirect_url = f'{login_url}?next={url}'
        assert response.status_code == 302
        assert response.url == redirect_url
        assert Comment.objects.count() == comments_before

    def test_authorized_user_can_send_comment(self, author_client, news, author):
        url = reverse('news:detail', args=(news.id,))
        comments_before = Comment.objects.count()
        form_data = {'text': 'Текст комментария'}
        response = author_client.post(url, data=form_data)
        assert response.status_code == 302
        assert response.url == url
        assert Comment.objects.count() == comments_before + 1
        new_comment = Comment.objects.latest('id')
        assert new_comment.text == form_data['text']
        assert new_comment.news == news
        assert new_comment.author == author

    def test_comment_with_bad_words_not_published(self, author_client, news):
        url = reverse('news:detail', args=(news.id,))
        comments_before = Comment.objects.count()
        bad_text = f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'
        form_data = {'text': bad_text}
        response = author_client.post(url, data=form_data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        assert Comment.objects.count() == comments_before

    def test_author_can_edit_comment(self, author_client, comment, news):
        url = reverse('news:edit', args=(comment.id,))
        new_text = 'Обновлённый текст комментария'
        form_data = {'text': new_text}
        response = author_client.post(url, data=form_data)
        assert response.status_code == 302
        assert response.url == reverse('news:detail', args=(news.id,))
        comment.refresh_from_db()
        assert comment.text == new_text

    def test_author_can_delete_comment(self, author_client, comment, news):
        url = reverse('news:delete', args=(comment.id,))
        comments_before = Comment.objects.count()
        response = author_client.post(url)
        assert response.status_code == 302
        assert response.url == reverse('news:detail', args=(news.id,))
        assert Comment.objects.count() == comments_before - 1

    def test_user_cant_edit_other_comment(self, not_author_client, comment):
        url = reverse('news:edit', args=(comment.id,))
        old_text = comment.text
        form_data = {'text': 'Попытка изменить чужой комментарий'}
        response = not_author_client.post(url, data=form_data)
        assert response.status_code == 403
        comment.refresh_from_db()
        assert comment.text == old_text

    def test_user_cant_delete_other_comment(self, not_author_client, comment):
        url = reverse('news:delete', args=(comment.id,))
        comments_before = Comment.objects.count()
        response = not_author_client.post(url)
        assert response.status_code == 403
        assert Comment.objects.count() == comments_before
