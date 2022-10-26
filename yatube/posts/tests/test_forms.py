import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User

SLUG = 'test-slug1'
SLUG2 = 'second-slug'
USERNAME = 'Dmitro1'
TEXT = 'Тестовый пост для форм'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'

INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
CREATE_URL = reverse('posts:post_create')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group2 = Group.objects.create(
            title='Птички',
            slug=SLUG2,
            description='блог о птичках')

        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT,
            group=cls.group,
        )

        cls.DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        posts_before_posting = list(Post.objects.values_list('id', flat=True))
        form_data = {
            'text': 'Ну какой-то вроде как текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count() - post_count, 1)
        created_posts = Post.objects.all().exclude(id__in=posts_before_posting)
        self.assertTrue(created_posts.count() == 1)
        post = created_posts[0]
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тут текст был изменён',
            'group': self.group2.id
        }
        response = self.authorized_client.post(
            self.EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.DETAIL_URL)

        edited_post = Post.objects.get(id=self.post.id)
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.author, self.post.author)
        self.assertEqual(Post.objects.count(), post_count)

    def test_post_edit_page_show_correct_context(self):
        """Шаблоны post_create и post_edit сформированы
         с правильными типами полей форм."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        urls = [
            CREATE_URL,
            self.EDIT_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                for fieldS, typeS in form_fields.items():
                    response = self.authorized_client.get(url)
                    self.assertIsInstance(response.context.get('form').fields.
                                          get(fieldS),
                                          typeS)
