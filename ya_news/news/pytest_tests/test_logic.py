import pytest
from django.urls import reverse
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_DATA = {'text': COMMENT_TEXT}
BAD_WORD_DATA = {'text': 'редиска'}

def test_anonymous_user_cant_send_comment(client, detail_url):
    comments_before = Comment.objects.count()
    response = client.post(detail_url, data=NEW_COMMENT_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assert response.status_code == 302
    assert response.url == expected_url
    assert Comment.objects.count() == comments_before

def test_authorized_user_can_send_comment(
        author_client, news, author, detail_url):
    comments_before = Comment.objects.count()
    response = author_client.post(detail_url, data=NEW_COMMENT_DATA)
    assert response.status_code == 302
    assert response.url == detail_url
    assert Comment.objects.count() == comments_before + 1

    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author

def test_comment_with_bad_words_not_published(author_client, detail_url):
    comments_before = Comment.objects.count()
    response = author_client.post(detail_url, data=BAD_WORD_DATA)
    assert Comment.objects.count() == comments_before
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors

def test_author_can_edit_comment(author_client, comment, news, edit_url, detail_url):
    response = author_client.post(edit_url, data=NEW_COMMENT_DATA)
    assert response.status_code == 302
    assert response.url == detail_url

    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == COMMENT_TEXT
    assert updated_comment.news == news
    assert updated_comment.author == comment.author

def test_author_can_delete_comment(author_client, comment, news, delete_url, detail_url):
    comments_before = Comment.objects.count()
    response = author_client.post(delete_url)
    assert response.status_code == 302
    assert response.url == detail_url
    assert Comment.objects.count() == comments_before - 1

def test_user_cant_edit_other_comment(not_author_client, comment, edit_url):
    original_text = comment.text
    response = not_author_client.post(edit_url, data=NEW_COMMENT_DATA)
    assert response.status_code == 403
    
    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == original_text

def test_user_cant_delete_other_comment(not_author_client, comment, delete_url):
    comments_before = Comment.objects.count()
    response = not_author_client.post(delete_url)
    assert response.status_code == 403
    assert Comment.objects.count() == comments_before
