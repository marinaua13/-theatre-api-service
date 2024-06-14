from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from catalog.models import TheatreHall
from catalog.serializers import TheatreHallSerializer
from django.contrib.auth import get_user_model


THEATRE_HALL_URL = reverse("catalog:theatrehall-list")


class PublicTheatreHallApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_theatre_halls(self):
        TheatreHall.objects.create(name="Main Hall", rows=10, seats_in_row=10)
        TheatreHall.objects.create(name="Side Hall", rows=5, seats_in_row=5)

        res = self.client.get(THEATRE_HALL_URL)

        TheatreHall.objects.all().order_by("name")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_theatre_hall_unauthorized(self):
        payload = {"name": "Main Hall", "rows": 10, "seats_in_row": 10}
        res = self.client.post(THEATRE_HALL_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTheatreHallApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "password123", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_theatre_hall(self):
        payload = {"name": "Main Hall", "rows": 10, "seats_in_row": 10}
        res = self.client.post(THEATRE_HALL_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        theatre_hall = TheatreHall.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(theatre_hall, key))

    def test_retrieve_theatre_hall(self):
        theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=10
        )
        url = reverse("catalog:theatrehall-detail", args=[theatre_hall.id])
        res = self.client.get(url)

        serializer = TheatreHallSerializer(theatre_hall)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
