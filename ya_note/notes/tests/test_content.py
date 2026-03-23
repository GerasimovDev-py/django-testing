from notes.forms import NoteForm
from notes.tests.base import (
    NOTES_LIST_URL, NOTES_ADD_URL, NOTES_EDIT_URL, BaseTestCase
)


class TestContent(BaseTestCase):

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, note_in_list in users_statuses:
            with self.subTest(client=client):
                response = client.get(NOTES_LIST_URL)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        urls = (NOTES_ADD_URL, NOTES_EDIT_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
