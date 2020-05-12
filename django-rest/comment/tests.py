import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from comment.models import Comment
from post.models import Post


class CommentListCreate(APITestCase):
    url = reverse('comment:create')
    url_login = reverse('token_obtain_pair')

    def setUp(self):
        self.username = 'meltem'
        self.password = 'sifre12345'
        self.post = Post.objects.create(title='This is title', content='this is content')
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.parent_comment = Comment.objects.create(content='this is my comment', user=self.user, post=self.post)
        self.test_user_token()

    def test_user_token(self):
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue('access' in json.loads(response.content))
        self.token = response.data['access']

        # sent token for every request:
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_add_parent_comment(self):
        data = {
            'content': 'this is my comment',
            'user': self.user.id,
            'post': self.post.id,
            'parent': ''
        }

        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_add_child_comment(self):
        data = {
            'content': 'this is my comment',
            'user': self.user.id,
            'post': self.post.id,
            'parent': self.parent_comment.id
        }

        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_comment_list(self):
        self.test_user_token()
        response = self.client.get(self.url, {'q': self.post.id})
        self.assertTrue(len(response.data) == Comment.objects.filter(post=self.post).count())


class CommentUpdateDeleteTest(APITestCase):
    url_login = reverse('token_obtain_pair')

    def setUp(self):
        self.username = 'meltem'
        self.password = 'sifre12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username='meltemk', password=self.password)
        self.post = Post.objects.create(title='This is title', content='this is content')
        self.comment = Comment.objects.create(content='this is my comment', user=self.user, post=self.post)

        # this part is different because we are calling update-delete url with an id number!
        self.url = reverse("comment:update", kwargs={'pk': self.comment.pk})
        self.test_user_token()

    def test_user_token(self, username='meltem', password='sifre12345'):
        data = {
            'username': username,
            'password': password
        }
        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue('access' in json.loads(response.content))
        self.token = response.data['access']

        # sent token for every request:
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_update_comment(self):
        data = {
            'content': 'this is my new content',
        }

        response = self.client.put(self.url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(Comment.objects.get(pk=self.comment.id).content == data['content'])

    def test_update_different_user_comment(self):
        self.test_user_token(self.user2)
        data = {
            'content': 'new content',
        }
        response = self.client.put(self.url_login)
        self.assertTrue(403, response.status_code)
        self.assertNotEqual(Comment.objects.get(pk=self.comment.id).content, 'new content')

    def test_delete_comment(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_comment_delete_different_user(self):
        self.test_user_token('meltemk')
        response = self.client.delete(self.url)
        self.assertEqual(403, response.status_code)
        self.assertTrue(Comment.objects.get(pk=self.comment.pk))

    def test_authorization(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)
