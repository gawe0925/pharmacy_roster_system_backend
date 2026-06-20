from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from shiftapp.models import LeaveRequest
from datetime import date

User = get_user_model()

# 建立 user 的 helper function，避免每次重複寫必填欄位
def make_user(username, email, password, is_manager=False, is_superuser=False):
    if is_superuser:
        return User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            is_manager=True,   
            gender='M',
            mobile='0400000000',
            address='123 Test St',
            suburb='Sydney',
            state='NSW',
            postcode='2000',
            tfn='123456789',
        )
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_manager=is_manager,
        gender='M',
        mobile='0400000000',
        address='123 Test St',
        suburb='Sydney',
        state='NSW',
        postcode='2000',
        tfn='123456789',
    )


class ShiftAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user('testuser', 'test@test.com', 'pass')

    def test_shift_list_requires_login(self):
        response = self.client.get('/shift/')
        self.assertEqual(response.status_code, 401)

    def test_shift_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/shift/')
        self.assertEqual(response.status_code, 200)


class MemberViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.superuser = make_user('super', 'super@test.com', 'pass', is_superuser=True)
        self.manager = make_user('manager', 'manager@test.com', 'pass', is_manager=True)
        self.staff = make_user('staff', 'staff@test.com', 'pass')

    def test_superuser_sees_all_members(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/member/')
        self.assertEqual(response.status_code, 200)
        emails = [m['email'] for m in response.data]
        self.assertIn('manager@test.com', emails)
        self.assertIn('staff@test.com', emails)

    def test_manager_cannot_see_superuser(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/member/')
        self.assertEqual(response.status_code, 200)
        emails = [m['email'] for m in response.data]
        self.assertNotIn('super@test.com', emails)

    def test_staff_only_sees_themselves(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/member/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'staff@test.com')


class LeaveRequestViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.superuser = make_user('super', 'super@test.com', 'pass', is_superuser=True)
        self.manager = make_user('manager', 'manager@test.com', 'pass', is_manager=True)
        self.staff_a = make_user('staff_a', 'staffa@test.com', 'pass')
        self.staff_b = make_user('staff_b', 'staffb@test.com', 'pass')

        self.leave_a = LeaveRequest.objects.create(
            staff=self.staff_a,
            leave_type='annual',
            start_date=date.today(),
        )
        self.leave_b = LeaveRequest.objects.create(
            staff=self.staff_b,
            leave_type='sick',
            start_date=date.today(),
        )

    def test_staff_only_sees_own_leave(self):
        self.client.force_authenticate(user=self.staff_a)
        response = self.client.get('/leaverequest/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.leave_a.id)

    def test_manager_sees_all_leave_except_superuser(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/leaverequest/')
        self.assertEqual(response.status_code, 200)
        ids = [l['id'] for l in response.data]
        self.assertIn(self.leave_a.id, ids)
        self.assertIn(self.leave_b.id, ids)

    def test_superuser_sees_all_leave(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/leaverequest/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)