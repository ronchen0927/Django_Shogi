from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class CheckLoginStatusViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')

    def test_check_login_api_view(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        url = reverse('check-login')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'status': 'Not logged in'})

        self.client.login(username='testuser', password='password')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'Logged in', 'user': self.user.username})