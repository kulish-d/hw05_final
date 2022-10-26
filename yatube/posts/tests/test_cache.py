from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, User

USERNAME = 'Dmitro-cache'
TEXT = 'Тестовый пост для кэша'

INDEX_URL = reverse('posts:index')


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.guest_client = Client()
        Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )

    def test_cache(self):
        response_1 = self.guest_client.get(INDEX_URL)
        Post.objects.create(
            text='Тут какой-то текст (любой)',
            author=self.user,
        )
        response_2 = self.guest_client.get(INDEX_URL)
        self.assertEqual(
            response_1.content,
            response_2.content
        )
        cache.clear()
        response_3 = self.guest_client.get(INDEX_URL)
        self.assertNotEqual(
            response_1.content,
            response_3.content
        )
