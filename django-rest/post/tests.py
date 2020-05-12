import json
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from post.models import Post


class TestPostListCreate(APITestCase):
    url_list = reverse('post:list')
    url_create = reverse('post:create')
    url_login = reverse('token_obtain_pair')

    def setUp(self):
        self.username = 'meltem'
        self.password = 'sifre12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
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

    def test_add_new_post(self):
        data = {
            'content': 'this is the content for the post',
            'title': 'this is the title of the post'
        }

        response = self.client.post(self.url_create, data)
        self.assertEqual(201, response.status_code)

    def test_add_new_post_unauthorizated_user(self):
        self.client.credentials()
        response = self.client.get(self.url_create)
        self.assertEqual(401, response.status_code)

    def test_list_posts(self):
        # add the first data to the empty database by calling this function:
        self.test_add_new_post()
        response = self.client.get(self.url_list)
        self.assertEqual(200, response.status_code)
        self.assertTrue(len(json.loads(response.content)['results']) == Post.objects.all().count())


class TestUpdateDelete(APITestCase):
    url = reverse('post:list')
    url_login = reverse('token_obtain_pair')

    def setUp(self):
        self.username = 'meltem'
        self.password = 'sifre12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        # user2 is required for checking update security
        self.user2 = User.objects.create_user(username='meltemk', password=self.password)
        self.post = Post.objects.create(title='This is title', content='this is content')

        # this part is different because we are calling update-delete url with an id number!
        self.url = reverse("post:update", kwargs={'slug': self.post.slug})
        self.test_user_token()

    # this is also different because we have to check if other users can change or delete my favourites:
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

    def test_post_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)

    def test_post_delete_different_user(self):
        self.test_user_token('meltemk')
        response = self.client.delete(self.url)
        self.assertEqual(403, response.status_code)

    def test_post_update(self):
        data = {
            'content': 'this is my content',
            'title': 'this is my title'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(json.loads(response.content)['content'] == data['content'])

    def test_post_update_different_user(self):
        self.test_user_token(self.user2)
        data = {
            'content': 'this is my content',
            'title': 'this is my title',
            'user': self.user2.id
        }
        response = self.client.put(self.url_login, data)
        self.assertTrue(403, response.status_code)

    def test_unauthorization(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(401, response.status_code)