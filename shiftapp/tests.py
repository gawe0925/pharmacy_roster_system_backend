from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from shiftapp.models import Shift

User = get_user_model()

class ShiftAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )

    def test_shift_list_requires_login(self):
        # 沒登入應該被擋下來
        response = self.client.get('/shift/')
        self.assertEqual(response.status_code, 401)

    def test_shift_list_authenticated(self):
        # 登入後可以拿到資料
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/shift/')
        self.assertEqual(response.status_code, 200)