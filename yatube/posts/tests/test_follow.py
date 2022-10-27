from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User, Follow

USERNAME1 = 'Dmitro-follow'
USERNAME2 = 'Grigorii-follow'
USERNAME3 = 'Oleg-follow'
TEXT = 'Тестовый пост для подписок'

INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.all().delete()
        Follow.objects.all().delete()
        cls.user1 = User.objects.create_user(username=USERNAME1)
        cls.author1 = Client()
        cls.author1.force_login(cls.user1)
        cls.author2 = Client()
        cls.user2 = User.objects.create_user(username=USERNAME2)
        cls.author2.force_login(cls.user2)
        cls.author3 = Client()
        cls.user3 = User.objects.create_user(username=USERNAME3)
        cls.author3.force_login(cls.user3)

        cls.FOLLOW_URL = reverse('posts:profile_follow', args=[cls.user1])
        cls.UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[cls.user1])

    def setUp(self):
        cache.clear()

    def test_follow_users(self):
        """Авторизованный пользователь может подписываться
         на других пользователей"""
        follow_count = Follow.objects.count()
        response = self.author2.get(self.FOLLOW_URL)
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(Follow.objects.filter(author=self.user1,
                                              user=self.user2))

    def test_unfollow_users(self):
        """Авторизованный пользователь может удалять подписки."""
        Follow.objects.get_or_create(
            author=self.user1,
            user=self.user2
        )
        response = self.author2.get(self.UNFOLLOW_URL)
        self.assertRedirects(response, INDEX_URL)
        self.assertFalse(Follow.objects.filter(author=self.user1,
                                               user=self.user2))

    def post_appears_in_index_followers(self):
        """Новая запись пользователя появляется в ленте тех,
         кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.author2.get(self.FOLLOW_URL)

        post = Post.objects.create(
            author=self.user1,
            text=TEXT,
        )

        self.assertEqual(
            self.author2.get(FOLLOW_INDEX_URL).context['page_obj'][0].text,
            post.text
        )

        self.assertNotContains(
            self.author2.get(FOLLOW_INDEX_URL).content, post
        )
