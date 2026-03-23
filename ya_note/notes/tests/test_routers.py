from http import HTTPStatus
from django.urls import reverse

from notes.tests.base import (
    NOTES_LIST_URL, NOTES_ADD_URL, NOTES_SUCCESS_URL, LOGIN_URL,
    NOTES_DETAIL_URL, NOTES_EDIT_URL, NOTES_DELETE_URL, BaseTestCase
)


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
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

    def test_logout_availability(self):
        url = reverse('users:logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_availability_for_authorized_user(self):
        urls = (NOTES_LIST_URL, NOTES_ADD_URL, NOTES_SUCCESS_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
