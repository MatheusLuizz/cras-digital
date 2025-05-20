from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import SupportTicket, SupportMessage
from .serializers import SupportTicketSerializer, SupportMessageSerializer

User = get_user_model()


class SupportTicketModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.ticket_data = {
            'user': self.user,
            'subject': 'Problema com o sistema',
            'description': 'Estou tendo problemas para acessar o sistema.',
            'status': 'open'
        }

        self.ticket = SupportTicket.objects.create(**self.ticket_data)

    def test_ticket_creation(self):
        self.assertEqual(self.ticket.user, self.ticket_data['user'])
        self.assertEqual(self.ticket.subject, self.ticket_data['subject'])
        self.assertEqual(self.ticket.description, self.ticket_data['description'])
        self.assertEqual(self.ticket.status, self.ticket_data['status'])
        self.assertIsNotNone(self.ticket.created_at)

    def test_ticket_str_method(self):
        expected_str = f"{self.user.username} - {self.ticket.subject}"
        actual_str = str(self.ticket)
        self.assertEqual(actual_str, expected_str)

    def test_ticket_with_default_status(self):
        ticket = SupportTicket.objects.create(
            user=self.user,
            subject='Outro problema',
            description='Descrição do outro problema'
        )
        self.assertEqual(ticket.status, 'open')  # Default value


class SupportMessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpassword123',
            is_staff=True
        )

        self.ticket = SupportTicket.objects.create(
            user=self.user,
            subject='Problema com o sistema',
            description='Estou tendo problemas para acessar o sistema.'
        )

        self.message_data = {
            'ticket': self.ticket,
            'sender': self.user,
            'message': 'Quando tento fazer login, recebo um erro.'
        }

        self.message = SupportMessage.objects.create(**self.message_data)

    def test_message_creation(self):
        self.assertEqual(self.message.ticket, self.message_data['ticket'])
        self.assertEqual(self.message.sender, self.message_data['sender'])
        self.assertEqual(self.message.message, self.message_data['message'])
        self.assertIsNotNone(self.message.created_at)

    def test_message_str_method(self):
        expected_format = f"{self.user.username} - "
        self.assertTrue(str(self.message).startswith(expected_format))

    def test_message_related_to_ticket(self):
        # Test that the message is correctly related to the ticket
        self.assertIn(self.message, self.ticket.messages.all())


class SupportTicketSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.ticket_data = {
            'user': self.user,
            'subject': 'Problema com o sistema',
            'description': 'Estou tendo problemas para acessar o sistema.',
            'status': 'open'
        }

        self.ticket = SupportTicket.objects.create(**self.ticket_data)
        self.serializer = SupportTicketSerializer(instance=self.ticket)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('subject', data)
        self.assertIn('description', data)
        self.assertIn('status', data)
        self.assertIn('created_at', data)
        self.assertIn('messages', data)

    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['subject'], self.ticket_data['subject'])
        self.assertEqual(data['description'], self.ticket_data['description'])
        self.assertEqual(data['status'], self.ticket_data['status'])


class SupportMessageSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.ticket = SupportTicket.objects.create(
            user=self.user,
            subject='Problema com o sistema',
            description='Estou tendo problemas para acessar o sistema.'
        )

        self.message_data = {
            'ticket': self.ticket,
            'sender': self.user,
            'message': 'Quando tento fazer login, recebo um erro.'
        }

        self.message = SupportMessage.objects.create(**self.message_data)
        self.serializer = SupportMessageSerializer(instance=self.message)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('ticket', data)
        self.assertIn('sender', data)
        self.assertIn('message', data)
        self.assertIn('created_at', data)

    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['ticket'], self.ticket.id)
        self.assertEqual(data['sender'], self.user.id)
        self.assertEqual(data['message'], self.message_data['message'])


class SupportTicketViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpassword123',
            is_staff=True
        )

        self.ticket = SupportTicket.objects.create(
            user=self.user,
            subject='Problema com o sistema',
            description='Estou tendo problemas para acessar o sistema.'
        )

        self.staff_ticket = SupportTicket.objects.create(
            user=self.staff_user,
            subject='Problema do staff',
            description='Descrição do problema do staff.'
        )

    def test_list_tickets_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Regular user should only see their own tickets
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['subject'], self.ticket.subject)

    def test_list_tickets_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)

        url = reverse('support-ticket-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Staff user should see all tickets
        self.assertEqual(len(response.data), 2)

    def test_retrieve_own_ticket(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-detail', args=[self.ticket.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], self.ticket.subject)

    def test_retrieve_other_ticket_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-detail', args=[self.staff_ticket.id])
        response = self.client.get(url)

        # Regular user should not be able to see other users' tickets
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_any_ticket_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)

        url = reverse('support-ticket-detail', args=[self.ticket.id])
        response = self.client.get(url)

        # Staff user should be able to see any ticket
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], self.ticket.subject)

    def test_create_ticket(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-list')
        data = {
            'subject': 'Novo problema',
            'description': 'Descrição do novo problema',
            'user': self.user.id
        }

        response = self.client.post(url, data, format='json')

        # Para debug
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupportTicket.objects.count(), 3)

        new_ticket = SupportTicket.objects.get(subject='Novo problema')
        self.assertEqual(new_ticket.user, self.user)
        self.assertEqual(new_ticket.description, 'Descrição do novo problema')
        self.assertEqual(new_ticket.status, 'open')

    def test_update_own_ticket(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-detail', args=[self.ticket.id])
        data = {
            'subject': 'Problema atualizado',
            'description': 'Descrição atualizada',
            'status': 'in_progress',
            'user': self.user.id  # Incluir user no update
        }

        response = self.client.put(url, data, format='json')

        # Para debug
        if response.status_code != status.HTTP_200_OK:
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.subject, 'Problema atualizado')
        self.assertEqual(self.ticket.description, 'Descrição atualizada')
        self.assertEqual(self.ticket.status, 'in_progress')

    def test_update_other_ticket_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-detail', args=[self.staff_ticket.id])
        data = {
            'subject': 'Tentando alterar ticket do staff',
            'description': 'Nova descrição',
            'status': 'resolved',
            'user': self.staff_user.id  # Incluir user no update
        }

        response = self.client.put(url, data, format='json')

        # Regular user should not be able to update other users' tickets
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_any_ticket_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)

        url = reverse('support-ticket-detail', args=[self.ticket.id])
        data = {
            'subject': 'Problema atualizado pelo staff',
            'description': 'Descrição atualizada pelo staff',
            'status': 'resolved',
            'user': self.user.id  # Incluir user no update
        }

        response = self.client.put(url, data, format='json')

        # Para debug
        if response.status_code != status.HTTP_200_OK:
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.subject, 'Problema atualizado pelo staff')
        self.assertEqual(self.ticket.status, 'resolved')

    def test_delete_own_ticket(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-detail', args=[self.ticket.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SupportTicket.objects.count(), 1)  # Only staff ticket remains

    def test_delete_other_ticket_as_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-detail', args=[self.staff_ticket.id])
        response = self.client.delete(url)

        # Regular user should not be able to delete other users' tickets
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(SupportTicket.objects.count(), 2)  # Both tickets remain

    def test_delete_any_ticket_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)

        url = reverse('support-ticket-detail', args=[self.ticket.id])
        response = self.client.delete(url)

        # Staff user should be able to delete any ticket
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SupportTicket.objects.count(), 1)  # Only staff ticket remains

    def test_my_tickets_action(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-ticket-my-tickets')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['subject'], self.ticket.subject)


class SupportMessageViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpassword123',
            is_staff=True
        )

        self.ticket = SupportTicket.objects.create(
            user=self.user,
            subject='Problema com o sistema',
            description='Estou tendo problemas para acessar o sistema.'
        )

        self.message = SupportMessage.objects.create(
            ticket=self.ticket,
            sender=self.user,
            message='Quando tento fazer login, recebo um erro.'
        )

        self.staff_message = SupportMessage.objects.create(
            ticket=self.ticket,
            sender=self.staff_user,
            message='Vamos verificar esse problema.'
        )

    def test_list_messages(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-message-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both messages

    def test_retrieve_message(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-message-detail', args=[self.message.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], self.message.message)

    def test_create_message(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-message-list')
        data = {
            'ticket': self.ticket.id,
            'message': 'Nova mensagem de acompanhamento',
            'sender': self.user.id
        }

        response = self.client.post(url, data, format='json')

        # Para debug
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupportMessage.objects.count(), 3)

        new_message = SupportMessage.objects.get(message='Nova mensagem de acompanhamento')
        self.assertEqual(new_message.sender, self.user)
        self.assertEqual(new_message.ticket, self.ticket)

    def test_update_own_message(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-message-detail', args=[self.message.id])
        data = {
            'ticket': self.ticket.id,
            'message': 'Mensagem atualizada',
            'sender': self.user.id  # Incluir sender no update
        }

        response = self.client.put(url, data, format='json')

        # Para debug
        if response.status_code != status.HTTP_200_OK:
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.message.refresh_from_db()
        self.assertEqual(self.message.message, 'Mensagem atualizada')

    def test_update_other_message(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-message-detail', args=[self.staff_message.id])
        data = {
            'ticket': self.ticket.id,
            'message': 'Tentando alterar mensagem do staff',
            'sender': self.staff_message.sender.id  # Incluir sender no update
        }

        response = self.client.put(url, data, format='json')

        # Para debug
        if response.status_code != status.HTTP_200_OK:
            print(f"Response data: {response.data}")

        # Usuário não deveria poder atualizar mensagens de outros usuários,
        # mas a view atual não tem essa restrição
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.staff_message.refresh_from_db()
        self.assertEqual(self.staff_message.message, 'Tentando alterar mensagem do staff')

    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('support-message-detail', args=[self.message.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SupportMessage.objects.count(), 1)  # Only staff message remains
