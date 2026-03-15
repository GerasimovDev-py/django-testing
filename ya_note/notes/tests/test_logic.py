from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):

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
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note'
        }

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(slug='new-note')
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_cannot_create_two_notes_with_same_slug(self):
        self.form_data['slug'] = self.note.slug
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(form, 'slug', self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug_auto_generated(self):
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.exclude(id=self.note.id).get()
        expected_slug = 'novaya-zametka'
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_edit_other_note(self):
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 404)
        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, 'Заголовок')
        self.assertEqual(unchanged_note.text, 'Текст')
        self.assertEqual(unchanged_note.slug, 'note-slug')
        self.assertEqual(unchanged_note.author, self.author)

    def test_user_cant_delete_other_note(self):
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        existing_note = Note.objects.get(id=self.note.id)
        self.assertEqual(existing_note.title, 'Заголовок')
        self.assertEqual(existing_note.text, 'Текст')
        self.assertEqual(existing_note.slug, 'note-slug')
        self.assertEqual(existing_note.author, self.author)
