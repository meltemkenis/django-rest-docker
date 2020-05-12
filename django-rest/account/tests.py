import json

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse


class UserRegistrationTestCase(APITestCase):
    url = reverse('account:register')
    url_login = reverse("token_obtain_pair")

    def test_user_registration(self):

        # User successfully registered with valid and correct datas.
        data = {
            'username': 'meltemtest',
            'password': 'deneme1234'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_user_invalid_password(self):

        # Try register with an invalid password
        data = {
            'username': 'meltemtest',
            'password': '1'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_uniq_user_name(self):

        # Check if the username for registration is unique or not. (it should be unique)
        self.test_user_registration()
        data = {
            'username': 'meltemtest',
            'password': 'deneme1234'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_user_authenticated_registration(self):

        # The user entering with session should not see the registration page
        self.test_user_registration()
        self.client.login(username='meltemtest', password='deneme1234')
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_user_authenticated_token_registration(self):

        # The user entering with token should not see the registration page
        self.test_user_registration()
        data = {
            'username': 'meltemtest',
            'password': 'deneme1234'
        }
        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response_2 = self.client.get(self.url)
        self.assertEqual(403, response_2.status_code)


class UserLogin(APITestCase):
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = 'meltem'
        self.password = 'deneme1234'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_user_token(self):
        response = self.client.post(self.url_login, {'username': 'meltem', 'password': 'deneme1234'})
        self.assertEqual(200, response.status_code)
        self.assertTrue('access' in json.loads(response.content))

    def test_user_invalid_data(self):
        response = self.client.post(self.url_login, {'username': 'asdfghjkl', 'password': 'deneme1234'})
        self.assertEqual(401, response.status_code)

    def test_user_empty_data(self):
        response = self.client.post(self.url_login, {'username': '', 'password': ''})
        self.assertEqual(400, response.status_code)


class UserPasswordChange(APITestCase):
    url = reverse('account:change-password')
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = 'meltem'
        self.password = 'deneme1234'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def login_with_token(self):
        data = {
            'username': 'meltem',
            'password': 'deneme1234'
        }
        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_is_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)

    def test_with_valid_information(self):
        self.login_with_token()
        data = {
            'old_password': 'deneme1234',
            'new_password': 'asdfgh1234',
        }
        response = self.client.put(self.url, data)
        self.assertEqual(204, response.status_code)

    def test_with_wrong_information(self):
        self.login_with_token()
        data = {
            'old_password': 'asdfgrty784',
            'new_password': 'asdfgh1234',
        }
        response = self.client.put(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_with_empty_information(self):
        self.login_with_token()
        data = {
            'old_password': '',
            'new_password': 'asdfgh1234',
        }
        response = self.client.put(self.url, data)
        self.assertEqual(400, response.status_code)


class UserProfileUpdate(APITestCase):
    url = reverse('account:me')
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = 'meltem'
        self.password = 'deneme1234'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def login_with_token(self):
        data = {
            'username': 'meltem',
            'password': 'deneme1234'
        }
        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_is_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)

    def test_with_valid_information(self):
        self.login_with_token()
        data = {
            "id": 1,
            "first_name": "",
            "last_name": "",
            "profile": {
                "id": 1,
                "note": "my notes",
                "twitter": "meltemsuperuser"
            }
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(json.loads(response.content), data)

    def test_with_empty_information(self):
        self.login_with_token()
        data = {
            "id": 1,
            "first_name": "",
            "last_name": "",
            "profile": {
                "id": 1,
                "note": "",
                "twitter": ""
            }
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(400, response.status_code)
