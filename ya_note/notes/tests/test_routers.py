from http import HTTPStatus

from django.urls import reverse

from notes.tests.base import (
    NOTES_ADD_URL,
    NOTES_LIST_URL,
    NOTES_SUCCESS_URL,
    BaseTestCase,
)


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        """Проверка доступности общедоступных страниц."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_authorized_user(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        urls = (NOTES_LIST_URL, NOTES_ADD_URL, NOTES_SUCCESS_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_author(self):
        """Автор имеет доступ к деталям, редактированию и удалению заметки."""
        urls = (
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_another_user(self):
        """Чужой пользователь не имеет доступа к чужим заметкам (404)."""
        urls = (
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Анонимного пользователя перенаправляет на страницу логина."""
        login_url = reverse('users:login')
        urls = (
            NOTES_LIST_URL,
            NOTES_ADD_URL,
            NOTES_SUCCESS_URL,
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
