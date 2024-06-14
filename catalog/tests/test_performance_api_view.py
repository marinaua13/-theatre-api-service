from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from catalog.models import Performance, Play, TheatreHall
from catalog.serializers import PerformanceListSerializer, PerformanceDetailSerializer
from django.contrib.auth import get_user_model
from django.db.models import Count, F

PERFORMANCE_URL = reverse('catalog:performance-list')


class PerformanceViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password123',
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_performances(self):
        play = Play.objects.create(title='Test Play', description='Test Description')
        theatre_hall = TheatreHall.objects.create(name='Main Hall', rows=10, seats_in_row=10)
        Performance.objects.create(play=play, theatre_hall=theatre_hall, show_time='2024-06-15T12:00:00Z')

        res = self.client.get(PERFORMANCE_URL)

        performances = Performance.objects.all().annotate(
            tickets_available=(
                F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
        ).order_by('-show_time')
        serializer = PerformanceListSerializer(performances, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_performance(self):
        play = Play.objects.create(title='Test Play', description='Test Description')
        theatre_hall = TheatreHall.objects.create(name='Main Hall', rows=10, seats_in_row=10)
        performance = Performance.objects.create(play=play, theatre_hall=theatre_hall, show_time='2024-06-15T12:00:00Z')

        url = reverse('catalog:performance-detail', args=[performance.id])
        res = self.client.get(url)

        serializer = PerformanceDetailSerializer(performance)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_performance(self):
        play = Play.objects.create(title='Test Play', description='Test Description')
        theatre_hall = TheatreHall.objects.create(name='Main Hall', rows=10, seats_in_row=10)

        payload = {
            'play': play.id,
            'theatre_hall': theatre_hall.id,
            'show_time': '2024-06-16 14:00:00+00:00'
        }
        res = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        performance = Performance.objects.get(id=res.data['id'])
        self.assertEqual(performance.play.id, payload['play'])
        self.assertEqual(performance.theatre_hall.id, payload['theatre_hall'])
        self.assertEqual(str(performance.show_time), payload['show_time'])

    def test_update_performance(self):
        play = Play.objects.create(title='Test Play', description='Test Description')
        theatre_hall = TheatreHall.objects.create(name='Main Hall', rows=10, seats_in_row=10)
        performance = Performance.objects.create(play=play, theatre_hall=theatre_hall, show_time='2024-06-15T12:00:00Z')

        payload = {
            'play': play.id,
            'theatre_hall': theatre_hall.id,
            'show_time': '2024-06-17 16:00:00+00:00'
        }
        url = reverse('catalog:performance-detail', args=[performance.id])
        res = self.client.put(url, payload)

        performance.refresh_from_db()

        self.assertEqual(str(performance.show_time), payload['show_time'])

    def test_delete_performance(self):
        play = Play.objects.create(title='Test Play', description='Test Description')
        theatre_hall = TheatreHall.objects.create(name='Main Hall', rows=10, seats_in_row=10)
        performance = Performance.objects.create(play=play, theatre_hall=theatre_hall, show_time='2024-06-15T12:00:00Z')

        url = reverse('catalog:performance-detail', args=[performance.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Performance.objects.filter(id=performance.id).exists())
