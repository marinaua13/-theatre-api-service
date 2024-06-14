from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from catalog.models import Genre
from django.contrib.auth import get_user_model

from catalog.serializers import GenreSerializer

GENRE_URL = reverse("catalog:genre-list")


class PublicGenreApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_genres_unauthorized(self):
        res = self.client.get(GENRE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGenreApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "password123", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_genre(self):
        payload = {"name": "Drama"}
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        genre = Genre.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(genre, key))
