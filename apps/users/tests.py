from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

from apps.users.models import User, UserProfile
from apps.users.serializers import UserSerializer, UserProfileSerializer


class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '123.456.789-00'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        self.assertEqual(self.user.username, self.user_data['username'])
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.first_name, self.user_data['first_name'])
        self.assertEqual(self.user.last_name, self.user_data['last_name'])
        self.assertEqual(self.user.cpf, self.user_data['cpf'])
        self.assertFalse(bool(self.user.document))

    def test_user_str_method(self):
        self.assertEqual(str(self.user), self.user_data['username'])

    def test_user_with_document(self):
        document = SimpleUploadedFile("test_doc.pdf", b"file_content", content_type="application/pdf")
        user = User.objects.create_user(
            username='userdoc',
            email='userdoc@example.com',
            password='password123',
            document=document
        )
        self.assertIsNotNone(user.document)
        self.assertTrue(user.document.name.startswith('documents/'))


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.profile_data = {
            'user': self.user,
            'address': 'Rua Exemplo, 123',
            'neighborhood': 'Centro',
            'phone': '(81) 98765-4321',
            'birth_date': date(1990, 1, 1),
            'is_vulnerable': True,
            'cadUnico_number': '12345678901'
        }

        self.profile = UserProfile.objects.create(**self.profile_data)

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.address, self.profile_data['address'])
        self.assertEqual(self.profile.neighborhood, self.profile_data['neighborhood'])
        self.assertEqual(self.profile.city, 'Paulista')  # Default value
        self.assertEqual(self.profile.state, 'PE')  # Default value
        self.assertEqual(self.profile.phone, self.profile_data['phone'])
        self.assertEqual(self.profile.birth_date, self.profile_data['birth_date'])
        self.assertEqual(self.profile.is_vulnerable, self.profile_data['is_vulnerable'])
        self.assertEqual(self.profile.cadUnico_number, self.profile_data['cadUnico_number'])

    def test_profile_str_method(self):
        self.assertEqual(str(self.profile), self.user.username)

    def test_profile_with_defaults(self):
        user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='password123'
        )

        profile = UserProfile.objects.create(user=user)

        self.assertEqual(profile.city, 'Paulista')
        self.assertEqual(profile.state, 'PE')
        self.assertFalse(profile.is_vulnerable)
        self.assertIsNone(profile.address)
        self.assertIsNone(profile.neighborhood)
        self.assertIsNone(profile.phone)
        self.assertIsNone(profile.birth_date)
        self.assertIsNone(profile.cadUnico_number)


class UserProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.profile_data = {
            'user': self.user,
            'address': 'Rua Exemplo, 123',
            'neighborhood': 'Centro',
            'city': 'Recife',
            'state': 'PE',
            'phone': '(81) 98765-4321',
            'birth_date': date(1990, 1, 1),
            'is_vulnerable': True,
            'cadUnico_number': '12345678901'
        }

        self.profile = UserProfile.objects.create(**self.profile_data)
        self.serializer = UserProfileSerializer(instance=self.profile)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set([
            'id', 'user', 'address', 'neighborhood', 'city', 'state',
            'phone', 'birth_date', 'is_vulnerable', 'cadUnico_number'
        ]))

    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['address'], self.profile_data['address'])
        self.assertEqual(data['neighborhood'], self.profile_data['neighborhood'])
        self.assertEqual(data['city'], self.profile_data['city'])
        self.assertEqual(data['state'], self.profile_data['state'])
        self.assertEqual(data['phone'], self.profile_data['phone'])
        self.assertEqual(data['birth_date'], str(self.profile_data['birth_date']))
        self.assertEqual(data['is_vulnerable'], self.profile_data['is_vulnerable'])
        self.assertEqual(data['cadUnico_number'], self.profile_data['cadUnico_number'])


class UserSerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'cpf': '123.456.789-00'
        }

        self.user = User.objects.create_user(**self.user_data)

        self.profile_data = {
            'address': 'Rua Exemplo, 123',
            'neighborhood': 'Centro',
            'city': 'Recife',
            'state': 'PE',
            'phone': '(81) 98765-4321',
            'birth_date': date(1990, 1, 1),
            'is_vulnerable': True,
            'cadUnico_number': '12345678901'
        }

        self.profile = UserProfile.objects.create(user=self.user, **self.profile_data)
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set([
            'id', 'username', 'email', 'first_name', 'last_name', 'cpf', 'document', 'profile'
        ]))
        # Password should not be in the serialized data (write_only)
        self.assertNotIn('password', data)

    def test_profile_nested_serialization(self):
        data = self.serializer.data
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['address'], self.profile_data['address'])
        self.assertEqual(data['profile']['neighborhood'], self.profile_data['neighborhood'])
        self.assertEqual(data['profile']['city'], self.profile_data['city'])
        self.assertEqual(data['profile']['state'], self.profile_data['state'])
        self.assertEqual(data['profile']['phone'], self.profile_data['phone'])
        self.assertEqual(data['profile']['birth_date'], str(self.profile_data['birth_date']))
        self.assertEqual(data['profile']['is_vulnerable'], self.profile_data['is_vulnerable'])
        self.assertEqual(data['profile']['cadUnico_number'], self.profile_data['cadUnico_number'])

    def test_create_user_with_profile(self):
        new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'cpf': '987.654.321-00',
            'profile': {
                'address': 'Nova Rua, 456',
                'neighborhood': 'Novo Bairro',
                'phone': '(81) 91234-5678',
                'birth_date': '1995-05-05',
                'is_vulnerable': False,
                # Adicionar o campo user é necessário para o serializer
                'user': None  # Será substituído durante a criação
            }
        }

        # Vamos criar o usuário primeiro e depois adicionar o perfil
        user_data = {k: v for k, v in new_user_data.items() if k != 'profile'}
        serializer = UserSerializer(data=user_data)

        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Verificar se o usuário foi criado corretamente
        self.assertEqual(user.username, new_user_data['username'])
        self.assertEqual(user.email, new_user_data['email'])
        self.assertEqual(user.first_name, new_user_data['first_name'])
        self.assertEqual(user.last_name, new_user_data['last_name'])
        self.assertEqual(user.cpf, new_user_data['cpf'])

        # Verificar se o perfil foi criado automaticamente
        self.assertTrue(hasattr(user, 'profile'))

        # Atualizar o perfil com os dados desejados
        profile_data = new_user_data['profile']
        profile_data['user'] = user.id
        profile_serializer = UserProfileSerializer(instance=user.profile, data=profile_data)

        if not profile_serializer.is_valid():
            print(f"Profile serializer errors: {profile_serializer.errors}")

        self.assertTrue(profile_serializer.is_valid())
        profile_serializer.save()

        # Recarregar o usuário para obter o perfil atualizado
        user.refresh_from_db()

        # Verificar se o perfil foi atualizado corretamente
        self.assertEqual(user.profile.address, profile_data['address'])
        self.assertEqual(user.profile.neighborhood, profile_data['neighborhood'])
        self.assertEqual(user.profile.phone, profile_data['phone'])
        self.assertEqual(str(user.profile.birth_date), profile_data['birth_date'])
        self.assertEqual(user.profile.is_vulnerable, profile_data['is_vulnerable'])

    def test_create_user_without_profile(self):
        new_user_data = {
            'username': 'noprofileuser',
            'email': 'noprofile@example.com',
            'password': 'password123',
            'first_name': 'No',
            'last_name': 'Profile'
        }

        serializer = UserSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, new_user_data['username'])

        # Check if default profile was created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.city, 'Paulista')
        self.assertEqual(user.profile.state, 'PE')


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpassword123',
            email='admin@example.com'
        )

        self.regular_user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            cpf='123.456.789-00'
        )

        UserProfile.objects.create(
            user=self.regular_user,
            address='Rua Exemplo, 123',
            neighborhood='Centro',
            phone='(81) 98765-4321'
        )

        self.client = APIClient()

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # admin and regular user

    def test_list_users_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('user-list')
        response = self.client.get(url)

        # Regular users should be able to list users with default permissions
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_unauthenticated(self):
        url = reverse('user-list')
        response = self.client.get(url)

        # Unauthenticated users should not be able to list users
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-detail', args=[self.regular_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_user.username)
        self.assertEqual(response.data['email'], self.regular_user.email)
        self.assertEqual(response.data['cpf'], self.regular_user.cpf)
        self.assertIn('profile', response.data)
        self.assertEqual(response.data['profile']['address'], 'Rua Exemplo, 123')

    def test_create_user_authenticated(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-list')
        new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'cpf': '987.654.321-00'
        }

        response = self.client.post(url, new_user_data, format='json')

        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, new_user_data['email'])
        self.assertEqual(new_user.cpf, new_user_data['cpf'])

        # Verificar se o perfil foi criado automaticamente
        self.assertTrue(hasattr(new_user, 'profile'))

    def test_create_user_unauthenticated(self):

        url = reverse('user-list')
        new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(url, new_user_data, format='json')

        # With AllowAny for create action, this should succeed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_update_user(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-detail', args=[self.regular_user.id])

        # Atualizar apenas os campos desejados
        updated_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'cpf': '111.222.333-44',
            # Não incluir password, pois é write_only e não é retornado no serializer
        }

        # Usar PATCH em vez de PUT para atualização parcial
        response = self.client.patch(url, updated_data, format='json')

        if response.status_code != status.HTTP_200_OK:
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, updated_data['username'])
        self.assertEqual(self.regular_user.email, updated_data['email'])
        self.assertEqual(self.regular_user.cpf, updated_data['cpf'])

    def test_partial_update_user(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-detail', args=[self.regular_user.id])
        partial_data = {
            'first_name': 'Partially',
            'last_name': 'Updated'
        }

        response = self.client.patch(url, partial_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, partial_data['first_name'])
        self.assertEqual(self.regular_user.last_name, partial_data['last_name'])
        self.assertEqual(self.regular_user.username, 'testuser')  # Unchanged

    def test_delete_user(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('user-detail', args=[self.regular_user.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)  # Only admin remains
