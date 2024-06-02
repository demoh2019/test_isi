from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Thread, Message

class ThreadTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')
        self.client.force_authenticate(user=self.user1)

    def test_create_thread(self):
        url = reverse('thread-list')
        data = {'participant2': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Thread.objects.count(), 1)
        self.assertEqual(Thread.objects.first().participant1, self.user1)
        self.assertEqual(Thread.objects.first().participant2, self.user2)

    def test_create_existing_thread(self):
        Thread.objects.create(participant1=self.user1, participant2=self.user2)
        url = reverse('thread-list')
        data = {'participant2': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Thread.objects.count(), 1)

    def test_get_threads(self):
        Thread.objects.create(participant1=self.user1, participant2=self.user2)
        Thread.objects.create(participant1=self.user1, participant2=self.user3)
        url = reverse('thread-list')
        response = self.client.get(url, format='json')
        results = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['participant2'], self.user2.id)
        self.assertEqual(results[1]['participant2'], self.user3.id)

    def test_delete_thread(self):
        thread = Thread.objects.create(participant1=self.user1, participant2=self.user2)
        url = reverse('thread-detail', kwargs={'pk': thread.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Thread.objects.count(), 0)


class MessageTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.client.force_authenticate(user=self.user1)
        self.thread = Thread.objects.create(participant1=self.user1, participant2=self.user2)

    def test_create_message(self):
        url = reverse('message-list', kwargs={'thread_id': self.thread.id})
        data = {'text': 'Hello', 'thread': self.thread.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().text, 'Hello')
        self.assertEqual(Message.objects.first().sender, self.user1)

    def test_get_messages(self):
        Message.objects.create(sender=self.user1, text='Hello', thread=self.thread)
        url = reverse('message-list', kwargs={'thread_id': self.thread.id})
        response = self.client.get(url, format='json')
        results = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'Hello')

    def test_mark_message_as_read(self):
        message = Message.objects.create(sender=self.user1, text='Hello', thread=self.thread)
        url = reverse('message-mark-as-read', kwargs={'pk': message.id})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_delete_message(self):
        message = Message.objects.create(sender=self.user1, text='Hello', thread=self.thread)
        url = reverse('message-detail', kwargs={'thread_id': self.thread.id, 'pk': message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Message.objects.count(), 0)

    def test_create_message_as_participant2(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('message-list', kwargs={'thread_id': self.thread.id})
        data = {'text': 'Hi from user2', 'thread': self.thread.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().text, 'Hi from user2')

    def test_create_message_invalid_thread(self):
        invalid_thread_id = self.thread.id + 1
        url = reverse('message-list', kwargs={'thread_id': invalid_thread_id})
        data = {'text': 'Invalid thread message', 'thread': invalid_thread_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_message_pagination(self):
        for i in range(15):
            Message.objects.create(sender=self.user1, text=f'Message {i+1}', thread=self.thread)

        url = reverse('message-list', kwargs={'thread_id': self.thread.id}) + '?limit=10&offset=0'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

        url = reverse('message-list', kwargs={'thread_id': self.thread.id}) + '?limit=10&offset=10'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)


class UnreadMessagesCountTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')
        self.client.force_authenticate(user=self.user1)
        self.thread = Thread.objects.create(participant1=self.user1, participant2=self.user2)

    def test_unread_messages_count(self):
        Message.objects.create(sender=self.user2, text='Hello', thread=self.thread, is_read=False)
        url = reverse('unread-messages-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_unread_messages_count_multiple_threads(self):
        thread2 = Thread.objects.create(participant1=self.user1, participant2=self.user3)
        Message.objects.create(sender=self.user2, text='Hello', thread=self.thread, is_read=False)
        Message.objects.create(sender=self.user3, text='Hi again', thread=thread2, is_read=False)
        url = reverse('unread-messages-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.protected_url = reverse('thread-list')

    def test_obtain_jwt_token(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_access_protected_endpoint_with_valid_token(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        protected_response = self.client.get(self.protected_url)
        self.assertEqual(protected_response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        protected_response = self.client.get(self.protected_url)
        self.assertEqual(protected_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_jwt_token(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data['refresh']

        refresh_response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_access_protected_endpoint_with_refreshed_token(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data['refresh']

        refresh_response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        new_access_token = refresh_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        protected_response = self.client.get(self.protected_url)
        self.assertEqual(protected_response.status_code, status.HTTP_200_OK)