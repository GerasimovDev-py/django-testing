from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_SUCCESS_URL = reverse('notes:success')


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
        cls.notes_detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.author_client = cls.client
        cls.author_client.force_login(cls.author)

        cls.reader_client = cls.client
        cls.reader_client.force_login(cls.reader)
