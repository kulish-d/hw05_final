from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User, Comment

USERNAME = 'Dmitro-com'
TEXT = 'Тестовый пост для комментариев'
TEXT_FOR_COMMENT = 'Это текст для тестового комментария'

LOGIN_URL = reverse('users:login')


class StaticCOMTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.all().delete()
        Comment.objects.all().delete()
        cls.guest = Client()
        cls.author = User.objects.create_user(username=USERNAME)
        cls.another = Client()
        cls.another.force_login(cls.author)

        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT,
        )

        cls.DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.COMMENT_REDIRECT_URL = f'{LOGIN_URL}?next={cls.COMMENT_URL}'

    def test_guest_cant_comment(self):
        """Комментировать посты может только авторизованный пользователь."""
        self.assertRedirects(
            self.guest.get(self.COMMENT_URL), self.COMMENT_REDIRECT_URL
        )

    def post_detail_contains_comment(self):
        """После успешной отправки комментарий появляется на странице поста."""
        form_data = {
            'text': TEXT_FOR_COMMENT,
        }
        self.another.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )

        self.assertIn(
            Comment.objects.get(text=form_data['text']),
            self.another.get(self.DETAIL_URL).context['comments']
        )
