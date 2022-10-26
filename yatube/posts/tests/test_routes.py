from django.test import TestCase
from django.urls import reverse

SLUG = 'test-slug2'
USERNAME = 'Dmitro2'
POST_ID = 1

URLS = (
    ('/', 'index', None),
    ('/create/', 'post_create', None),
    (f'/group/{SLUG}/', 'group_list', (SLUG,)),
    (f'/profile/{USERNAME}/', 'profile', (USERNAME,)),
    (f'/posts/{POST_ID}/', 'post_detail', (POST_ID,)),
    (f'/posts/{POST_ID}/edit/', 'post_edit', (POST_ID,)),
)


class StaticURLTests(TestCase):
    def test_route(self):
        """Расчеты дают ожидаемые в тз явные урлы"""
        for expected, real, args in URLS:
            with self.subTest():
                self.assertEqual(
                    expected, reverse(f'posts:{real}', args=args)
                )
