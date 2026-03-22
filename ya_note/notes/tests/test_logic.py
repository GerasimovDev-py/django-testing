from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from .base import BaseTestCase, NOTES_ADD_URL, NOTES_SUCCESS_URL


class TestLogic(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note'
        }
        cls.original_note_data = {
            'title': cls.note.title,
            'text': cls.note.text,
            'slug': cls.note.slug,
            'author': cls.note.author
        }

    def test_anonymous_user_cant_create_note(self):
        url = NOTES_ADD_URL
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note(self):
        notes_before = set(Note.objects.all())
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        notes_after = set(Note.objects.all())
        new_notes = notes_after - notes_before
        self.assertEqual(len(new_notes), 1)
        new_note = new_notes.pop()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_cannot_create_two_notes_with_same_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        form = response.context['form']
        self.assertFormError(form, 'slug', self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug_auto_generated(self):
        self.form_data.pop('slug')
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        new_note = Note.objects.exclude(id=self.note.id).get()
        expected_slug = 'novaya-zametka'
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        notes_before = set(Note.objects.all())
        response = self.author_client.post(
            self.notes_edit_url, data=self.form_data
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        notes_after = set(Note.objects.all())
        self.assertEqual(notes_before, notes_after)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.notes_delete_url)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_edit_other_note(self):
        notes_before = set(Note.objects.all())
        response = self.reader_client.post(
            self.notes_edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, 404)
        notes_after = set(Note.objects.all())
        self.assertEqual(notes_before, notes_after)
        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, self.original_note_data['title'])
        self.assertEqual(unchanged_note.text, self.original_note_data['text'])
        self.assertEqual(unchanged_note.slug, self.original_note_data['slug'])
        self.assertEqual(unchanged_note.author, self.original_note_data['author'])

    def test_user_cant_delete_other_note(self):
        notes_before = set(Note.objects.all())
        response = self.reader_client.post(self.notes_delete_url)
        self.assertEqual(response.status_code, 404)
        notes_after = set(Note.objects.all())
        self.assertEqual(notes_before, notes_after)
        existing_note = Note.objects.get(id=self.note.id)
        self.assertEqual(existing_note.title, self.original_note_data['title'])
        self.assertEqual(existing_note.text, self.original_note_data['text'])
        self.assertEqual(existing_note.slug, self.original_note_data['slug'])
        self.assertEqual(existing_note.author, self.original_note_data['author'])
