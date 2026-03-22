from notes.forms import NoteForm
from notes.tests.base import NOTES_ADD_URL, NOTES_LIST_URL, BaseTestCase


class TestContent(BaseTestCase):

    def test_note_in_object_list_for_author(self):
        response = self.author_client.get(NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_other_user_notes_not_in_list(self):
        response = self.reader_client.get(NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        urls = (NOTES_ADD_URL, self.notes_edit_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'], NoteForm
                )
