from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta

from apps.appointments.models import Appointment
from apps.appointments.permissions import IsOwnerOrProfessional

User = get_user_model()


class AppointmentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )
        self.professional = User.objects.create_user(
            username='professional',
            password='profpassword123',
            email='prof@example.com'
        )
        # Adicionar role ao professional
        self.professional.role = 'professional'
        self.professional.save()

        self.tomorrow = date.today() + timedelta(days=1)
        self.appointment_time = time(10, 0)  # 10:00 AM

    def test_appointment_creation(self):
        appointment = Appointment.objects.create(
            user=self.user,
            professional=self.professional,
            date=self.tomorrow,
            time=self.appointment_time,
            description="Consulta de teste"
        )

        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.professional, self.professional)
        self.assertEqual(appointment.date, self.tomorrow)
        self.assertEqual(appointment.time, self.appointment_time)
        self.assertEqual(appointment.status, 'pending')
        self.assertEqual(appointment.description, "Consulta de teste")

    def test_appointment_str_method(self):
        appointment = Appointment.objects.create(
            user=self.user,
            professional=self.professional,
            date=self.tomorrow,
            time=self.appointment_time
        )

        expected_str = f"Agendamento de {self.user} para {self.tomorrow} às {self.appointment_time}"
        self.assertEqual(str(appointment), expected_str)


class IsOwnerOrProfessionalPermissionTests(TestCase):
    def setUp(self):
        self.permission = IsOwnerOrProfessional()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )

        self.professional = User.objects.create_user(
            username='professional',
            password='profpassword123',
            email='prof@example.com'
        )
        # Adicionar role ao professional
        self.professional.role = 'professional'
        self.professional.save()

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword123',
            email='other@example.com'
        )

        self.tomorrow = date.today() + timedelta(days=1)
        self.appointment = Appointment.objects.create(
            user=self.user,
            professional=self.professional,
            date=self.tomorrow,
            time=time(10, 0)
        )

    def test_owner_has_permission(self):
        # Simular request
        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(self.user)

        # Testar permissão
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.appointment)
        )

    def test_professional_has_permission(self):
        # Simular request
        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(self.professional)

        # Testar permissão
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.appointment)
        )

    def test_other_user_has_no_permission(self):
        # Simular request
        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(self.other_user)

        # Testar permissão
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.appointment)
        )


class AppointmentViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )

        self.professional = User.objects.create_user(
            username='professional',
            password='profpassword123',
            email='prof@example.com'
        )
        # Adicionar role ao professional
        self.professional.role = 'professional'
        self.professional.save()

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword123',
            email='other@example.com'
        )

        self.tomorrow = date.today() + timedelta(days=1)
        self.appointment_time = time(10, 0)

        self.appointment = Appointment.objects.create(
            user=self.user,
            professional=self.professional,
            date=self.tomorrow,
            time=self.appointment_time,
            description="Consulta de teste"
        )

        self.other_appointment = Appointment.objects.create(
            user=self.other_user,
            professional=self.professional,
            date=self.tomorrow,
            time=time(14, 0),
            description="Outra consulta"
        )

        self.client = APIClient()

    def test_create_appointment_authenticated(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-list')
        data = {
            'date': self.tomorrow.strftime('%Y-%m-%d'),
            'time': '11:00:00',
            'description': 'Nova consulta'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 3)
        self.assertEqual(Appointment.objects.filter(user=self.user).count(), 2)

    def test_create_appointment_unauthenticated(self):
        url = reverse('appointment-list')
        data = {
            'date': self.tomorrow.strftime('%Y-%m-%d'),
            'time': '11:00:00',
            'description': 'Nova consulta'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_appointments_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Apenas os próprios agendamentos

    def test_list_appointments_as_professional(self):
        self.client.force_authenticate(user=self.professional)

        url = reverse('appointment-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Todos os agendamentos

    def test_retrieve_own_appointment(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-detail', args=[self.appointment.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.appointment.id)

    def test_retrieve_other_appointment_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-detail', args=[self.other_appointment.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_any_appointment_as_professional(self):
        self.client.force_authenticate(user=self.professional)

        url = reverse('appointment-detail', args=[self.other_appointment.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.other_appointment.id)

    def test_update_own_appointment(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-detail', args=[self.appointment.id])
        data = {
            'date': self.tomorrow.strftime('%Y-%m-%d'),
            'time': '15:00:00',
            'description': 'Consulta atualizada'
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(str(self.appointment.time), '15:00:00')
        self.assertEqual(self.appointment.description, 'Consulta atualizada')

    def test_update_other_appointment_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-detail', args=[self.other_appointment.id])
        data = {
            'date': self.tomorrow.strftime('%Y-%m-%d'),
            'time': '15:00:00',
            'description': 'Consulta atualizada'
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_appointment(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-detail', args=[self.appointment.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.filter(id=self.appointment.id).count(), 0)

    def test_delete_other_appointment_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('appointment-detail', args=[self.other_appointment.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Appointment.objects.filter(id=self.other_appointment.id).count(), 1)
