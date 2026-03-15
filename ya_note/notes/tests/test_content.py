from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )
        cls.notes_list_url = reverse('notes:list')
        cls.notes_add_url = reverse('notes:add')
        cls.notes_success_url = reverse('notes:success')
        cls.notes_detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_delete_url = reverse('notes:delete', args=(cls.note.slug,))


class TestContent(BaseTestCase):

    def test_note_in_object_list_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(self.notes_list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_other_user_notes_not_in_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.notes_list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        urls = (
            self.notes_add_url,
            self.notes_edit_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

