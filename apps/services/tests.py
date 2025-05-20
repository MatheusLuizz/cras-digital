from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model

from apps.services.models import Service
from apps.services.serializers import ServiceSerializer

User = get_user_model()


class ServiceModelTests(TestCase):
    def setUp(self):
        self.service_data = {
            'name': 'Atendimento Psicossocial',
            'description': 'Atendimento com psicólogo e assistente social',
            'duration_minutes': 60,
            'location': 'CRAS Centro'
        }

    def test_service_creation(self):
        service = Service.objects.create(**self.service_data)

        self.assertEqual(service.name, self.service_data['name'])
        self.assertEqual(service.description, self.service_data['description'])
        self.assertEqual(service.duration_minutes, self.service_data['duration_minutes'])
        self.assertEqual(service.location, self.service_data['location'])

    def test_service_str_method(self):
        service = Service.objects.create(**self.service_data)

        self.assertEqual(str(service), self.service_data['name'])


class ServiceSerializerTests(TestCase):
    def setUp(self):
        self.service_data = {
            'name': 'Atendimento Psicossocial',
            'description': 'Atendimento com psicólogo e assistente social',
            'duration_minutes': 60,
            'location': 'CRAS Centro'
        }
        self.service = Service.objects.create(**self.service_data)
        self.serializer = ServiceSerializer(instance=self.service)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name', 'description', 'duration_minutes', 'location']))

    def test_name_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['name'], self.service_data['name'])

    def test_description_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['description'], self.service_data['description'])

    def test_duration_minutes_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['duration_minutes'], self.service_data['duration_minutes'])

    def test_location_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['location'], self.service_data['location'])

    def test_serializer_validation(self):
        # Teste com dados válidos
        valid_serializer = ServiceSerializer(data=self.service_data)
        self.assertTrue(valid_serializer.is_valid())

        # Teste com dados inválidos (nome muito longo)
        invalid_data = self.service_data.copy()
        invalid_data['name'] = 'A' * 101  # Excede o max_length de 100
        invalid_serializer = ServiceSerializer(data=invalid_data)
        self.assertFalse(invalid_serializer.is_valid())
        self.assertIn('name', invalid_serializer.errors)

        # Teste com dados inválidos (duração negativa)
        invalid_data = self.service_data.copy()
        invalid_data['duration_minutes'] = -10
        invalid_serializer = ServiceSerializer(data=invalid_data)
        self.assertFalse(invalid_serializer.is_valid())
        self.assertIn('duration_minutes', invalid_serializer.errors)


class ServiceViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpassword123',
            email='admin@example.com'
        )

        self.regular_user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )

        self.service_data = {
            'name': 'Atendimento Psicossocial',
            'description': 'Atendimento com psicólogo e assistente social',
            'duration_minutes': 60,
            'location': 'CRAS Centro'
        }

        self.service = Service.objects.create(**self.service_data)

        self.client = APIClient()

    def test_list_services_authenticated(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('service-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.service_data['name'])

    def test_list_services_unauthenticated(self):
        url = reverse('service-list')
        response = self.client.get(url)

        # Como você está usando IsAuthenticatedOrReadOnly, usuários não autenticados podem ler
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.service_data['name'])

    def test_retrieve_service_authenticated(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('service-detail', args=[self.service.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.service_data['name'])
        self.assertEqual(response.data['description'], self.service_data['description'])
        self.assertEqual(response.data['duration_minutes'], self.service_data['duration_minutes'])
        self.assertEqual(response.data['location'], self.service_data['location'])

    def test_retrieve_service_unauthenticated(self):
        url = reverse('service-detail', args=[self.service.id])
        response = self.client.get(url)

        # Como você está usando IsAuthenticatedOrReadOnly, usuários não autenticados podem ler
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.service_data['name'])

    def test_create_service_authenticated(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('service-list')
        new_service_data = {
            'name': 'Cadastro Único',
            'description': 'Cadastramento para programas sociais',
            'duration_minutes': 45,
            'location': 'CRAS Maranguape'
        }

        response = self.client.post(url, new_service_data, format='json')

        # Com IsAuthenticatedOrReadOnly, usuários autenticados podem criar
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 2)

        new_service = Service.objects.get(name='Cadastro Único')
        self.assertEqual(new_service.description, new_service_data['description'])
        self.assertEqual(new_service.duration_minutes, new_service_data['duration_minutes'])
        self.assertEqual(new_service.location, new_service_data['location'])

    def test_create_service_unauthenticated(self):
        url = reverse('service-list')
        new_service_data = {
            'name': 'Cadastro Único',
            'description': 'Cadastramento para programas sociais',
            'duration_minutes': 45,
            'location': 'CRAS Maranguape'
        }

        response = self.client.post(url, new_service_data, format='json')

        # Com IsAuthenticatedOrReadOnly, usuários não autenticados não podem criar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Service.objects.count(), 1)

    def test_update_service_authenticated(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('service-detail', args=[self.service.id])
        updated_data = {
            'name': 'Atendimento Psicossocial Atualizado',
            'description': 'Descrição atualizada',
            'duration_minutes': 75,
            'location': 'CRAS Centro - Sala 2'
        }

        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.service.refresh_from_db()
        self.assertEqual(self.service.name, updated_data['name'])
        self.assertEqual(self.service.description, updated_data['description'])
        self.assertEqual(self.service.duration_minutes, updated_data['duration_minutes'])
        self.assertEqual(self.service.location, updated_data['location'])

    def test_update_service_unauthenticated(self):
        url = reverse('service-detail', args=[self.service.id])
        updated_data = {
            'name': 'Atendimento Psicossocial Atualizado',
            'description': 'Descrição atualizada',
            'duration_minutes': 75,
            'location': 'CRAS Centro - Sala 2'
        }

        response = self.client.put(url, updated_data, format='json')

        # Com IsAuthenticatedOrReadOnly, usuários não autenticados não podem atualizar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.service.refresh_from_db()
        self.assertEqual(self.service.name, self.service_data['name'])  # Não deve mudar

    def test_partial_update_service_authenticated(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('service-detail', args=[self.service.id])
        partial_data = {
            'duration_minutes': 90
        }

        response = self.client.patch(url, partial_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.service.refresh_from_db()
        self.assertEqual(self.service.name, self.service_data['name'])  # Não alterado
        self.assertEqual(self.service.duration_minutes, 90)  # Alterado

    def test_partial_update_service_unauthenticated(self):
        url = reverse('service-detail', args=[self.service.id])
        partial_data = {
            'duration_minutes': 90
        }

        response = self.client.patch(url, partial_data, format='json')

        # Com IsAuthenticatedOrReadOnly, usuários não autenticados não podem atualizar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.service.refresh_from_db()
        self.assertEqual(self.service.duration_minutes, self.service_data['duration_minutes'])  # Não deve mudar

    def test_delete_service_authenticated(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('service-detail', args=[self.service.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Service.objects.count(), 0)

    def test_delete_service_unauthenticated(self):
        url = reverse('service-detail', args=[self.service.id])
        response = self.client.delete(url)

        # Com IsAuthenticatedOrReadOnly, usuários não autenticados não podem deletar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Service.objects.count(), 1)  # O serviço ainda deve existir
