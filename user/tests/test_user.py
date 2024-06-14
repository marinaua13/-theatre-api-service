from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from user.serializers import UserSerializer

User = get_user_model()


class UserManagerTests(APITestCase):

    def test_create_user(self):
        email = "user@example.com"
        password = "testpass123"
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        email = "admin@example.com"
        password = "adminpass123"
        user = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")


class UserSerializerTests(APITestCase):

    def test_create_user(self):
        email = "user@example.com"
        password = "testpass123"
        serializer = UserSerializer(data={"email": email, "password": password})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_update_user_password(self):
        user = User.objects.create_user(email="user@example.com", password="oldpass123")
        serializer = UserSerializer(user, data={"password": "newpass123"}, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertTrue(user.check_password("newpass123"))


class UserViewsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )
        self.superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

    def test_register_user(self):
        url = reverse("user:create")
        data = {"email": "newuser@example.com", "password": "newpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        new_user = User.objects.get(email="newuser@example.com")
        self.assertTrue(new_user.check_password("newpass123"))
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)

    def test_token_obtain_pair(self):
        url = reverse("user:token_obtain_pair")
        data = {"email": self.user.email, "password": "testpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_manage_user(self):
        url = reverse("user:manage")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
