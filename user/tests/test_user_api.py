from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def setUp(self):
        self.email = "admin1@admin.com"
        self.password = "admin123456"

    def test_create_user(self):
        is_staff = False

        user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password
        )

        self.assertEqual(self.email, user.email)
        self.assertTrue(
            self.password,
            user.check_password(self.password)
        )
        self.assertEqual(is_staff, user.is_staff)

    def test_create_superuser(self):
        is_staff = True
        is_superuser = True

        user = get_user_model().objects.create_superuser(
            email=self.email,
            password=self.password
        )

        self.assertEqual(self.email, user.email)
        self.assertTrue(
            self.password,
            user.check_password(self.password)
        )
        self.assertEqual(is_staff, user.is_staff)
        self.assertEqual(is_superuser, user.is_superuser)