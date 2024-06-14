from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from catalog.models import Reservation, Ticket, Performance, Play, TheatreHall
from catalog.serializers import ReservationSerializer, ReservationListSerializer
from django.contrib.auth import get_user_model


RESERVATION_URL = reverse('catalog:reservation-list')

User = get_user_model()


class ReservationApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass'
        )
        self.client.force_authenticate(self.user)

    def create_performance_and_tickets(self):
        play = Play.objects.create(title='Test Play', description='Test Description')
        theatre_hall = TheatreHall.objects.create(name='Main Hall', rows=10, seats_in_row=20)
        performance = Performance.objects.create(play=play, theatre_hall=theatre_hall, show_time=timezone.now())
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(row=1, seat=1, performance=performance, reservation=reservation)
        return performance

    def test_list_reservations(self):
        performance = self.create_performance_and_tickets()
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(row=1, seat=2, performance=performance, reservation=reservation)

        res = self.client.get(RESERVATION_URL)
        reservations = Reservation.objects.filter(user=self.user)
        serializer = ReservationListSerializer(reservations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)
        self.assertEqual(res.data['results'], serializer.data)

    def test_list_reservations_unauthenticated(self):
        self.client.force_authenticate(None)
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation_unauthenticated(self):
        self.client.force_authenticate(None)
        performance = self.create_performance_and_tickets()

        payload = {
            'tickets': [
                {
                    'row': 1,
                    'seat': 1,
                    'performance': performance.id
                }
            ]
        }
        res = self.client.post(RESERVATION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation_invalid_ticket(self):
        performance = self.create_performance_and_tickets()

        payload = {
            'tickets': [
                {
                    'row': 100,
                    'seat': 100,
                    'performance': performance.id
                }
            ]
        }
        res = self.client.post(RESERVATION_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
