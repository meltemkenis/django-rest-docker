import json
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from favourite.models import Favourite
from post.models import Post


class FavouriteCreateList(APITestCase):
    url = reverse('favourite:list-create')
    url_login = reverse('token_obtain_pair')

    def setUp(self):
        self.username = 'meltem'
        self.password = 'sifre12345'
        self.post = Post.objects.create(title='This is title', content='this is content')
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

    def test_add_favourite(self):
        data = {
            'content': self.post.content,
            'user': self.user.id,
            'post': self.post.id
        }

        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_add_favourites(self):
        self.test_add_favourite()
        response = self.client.get(self.url)
        self.assertTrue(len(json.loads(response.content)['results']) == Favourite.objects.filter(user=self.user).count())


class FavouriteUpdateDelete(APITestCase):
    url_login = reverse('token_obtain_pair')

    def setUp(self):
        self.username = 'meltem'
        self.password = 'sifre12345'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username='meltemk', password=self.password)
        self.post = Post.objects.create(title='This is title', content='this is content')
        self.favourite = Favourite.objects.create(content='deneme', post=self.post, user=self.user)

        # this part is different because we are calling update-delete url with an id number!
        self.url = reverse("favourite:update-delete", kwargs={'pk': self.favourite.pk})
        self.test_user_token()

    # this is also different because we have to check if other users can change or delete my favourites:
    def test_user_token(self, username='meltem', password='sifre12345'):
        data = {
            'username': username,
            'password': password
        }
        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue('access' in json.loads(response .content))
        self.token = response.data['access']

        # sent token for every request:
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_fav_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)

    def test_fav_delete_different_user(self):
        self.test_user_token('meltemk')
        response = self.client.delete(self.url)
        self.assertEqual(403, response.status_code)

    def test_fav_update(self):
        data = {
            'content': 'this is my content',
        }

        response = self.client.put(self.url, data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(Favourite.objects.get(id=self.favourite.id).content == data['content'])

    def test_fav_update_different_user(self):
        self.test_user_token(self.user2)
        data = {
            'content': 'this is my content',
            'user': self.user2.id
        }
        response = self.client.put(self.url_login, data)
        self.assertTrue(403, response.status_code)

    def test_unauthorization(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(401, response.status_code)
