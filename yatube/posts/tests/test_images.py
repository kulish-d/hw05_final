import shutil
import tempfile

from django.core.cache import cache
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

SLUG = 'test-slug-img'
SLUG2 = 'second-slug-img'
USERNAME = 'Dmitro-img'
TEXT = 'Тестовый пост для картинок'
TITLE = 'Тестовая группа для картинок'
DESCRIPTION = 'Тестовое описание для картинок'

INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
CREATE_URL = reverse('posts:post_create')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class IMGTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.all().delete()
        Post.objects.all().delete()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.form_data = {
            'text': TEXT,
            'image': cls.uploaded,
        }

        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

        cls.DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        self.uploaded.seek(0)
        cache.clear()

    def test_add_record_database_postform(self):
        """При отправке поста с картинкой через форму PostForm
         создаётся запись в базе данных."""
        count_posts = Post.objects.count()
        posts_before_posting = list(Post.objects.values_list('id', flat=True))
        response = self.authorized_client.post(
            CREATE_URL,
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(
            Post.objects.all().exclude(id__in=posts_before_posting).exists()
        )

    def test_image_post_detail(self):
        self.assertEqual(
            self.authorized_client.get(self.DETAIL_URL)
            .context['post'].image, f'posts/{self.uploaded}'
        )

    def test_context_contains_image(self):
        """При выводе поста с картинкой изображение
         передаётся в словаре context."""
        URLS = (
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
        )
        for address in URLS:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.context['page_obj'][0].image,
                                 f'posts/{self.uploaded}')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
