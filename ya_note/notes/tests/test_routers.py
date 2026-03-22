from http import HTTPStatus

from django.urls import reverse

from .base import BaseTestCase, NOTES_LIST_URL, NOTES_ADD_URL, NOTES_SUCCESS_URL


class TestRoutes(BaseTestCase):

    def test_pages_availability_for_anonymous_user(self):
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

        logout_url = reverse('users:logout')
        response = self.client.get(logout_url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        response = self.client.post(logout_url)
        self.assertIn(response.status_code, [HTTPStatus.OK, HTTPStatus.FOUND])

    def test_pages_availability_for_auth_user(self):
        urls = (
            NOTES_LIST_URL,
            NOTES_ADD_URL,
            NOTES_SUCCESS_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_author(self):
        urls = (
            self.notes_detail_url,
            self.notes_edit_url,
            self.notes_delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_another_user(self):
        urls = (
            self.notes_detail_url,
            self.notes_edit_url,
            self.notes_delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            NOTES_LIST_URL,
            NOTES_ADD_URL,
            NOTES_SUCCESS_URL,
            self.notes_detail_url,
            self.notes_edit_url,
            self.notes_delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
