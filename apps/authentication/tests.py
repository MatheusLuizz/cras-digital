from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email='test@example.com'
        )

        self.client = APIClient()

    def test_token_obtain(self):

        url = reverse('token_obtain_pair')
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):

        obtain_url = reverse('token_obtain_pair')
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(obtain_url, data, format='json')
        refresh_token = response.data['refresh']

        refresh_url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_verify(self):

        obtain_url = reverse('token_obtain_pair')
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(obtain_url, data, format='json')
        access_token = response.data['access']

        verify_url = reverse('token_verify')
        data = {'token': access_token}
        response = self.client.post(verify_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_verify(self):

        verify_url = reverse('token_verify')
        data = {'token': 'invalid_token'}
        response = self.client.post(verify_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_credentials(self):

        url = reverse('token_obtain_pair')
        data = {
            'username': self.username,
            'password': 'wrong_password'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
