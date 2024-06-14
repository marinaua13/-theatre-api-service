from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from catalog.models import Actor
from catalog.serializers import ActorSerializer
from django.contrib.auth import get_user_model


ACTOR_URL = reverse('catalog:actor-list')


class PublicActorApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_actors_unauthorized(self):
        """Test that unauthorized user cannot retrieve actors"""
        res = self.client.get(ACTOR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_actor_unauthorized(self):
        """Test that unauthorized user cannot create an actor"""
        payload = {'first_name': 'John', 'last_name': 'Doe'}
        res = self.client.post(ACTOR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateActorApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password123',
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_actors(self):
        """Test retrieving a list of actors"""
        Actor.objects.create(first_name='John', last_name='Doe')
        Actor.objects.create(first_name='Jane', last_name='Doe')

        res = self.client.get(ACTOR_URL)

        actors = Actor.objects.all().order_by('last_name')
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_actor(self):
        """Test creating an actor"""
        payload = {'first_name': 'John', 'last_name': 'Doe'}
        res = self.client.post(ACTOR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        actor = Actor.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(actor, key))

    def test_retrieve_actor(self):
        """Test retrieving an actor by ID"""
        actor = Actor.objects.create(first_name='John', last_name='Doe')
        url = reverse('catalog:actor-detail', args=[actor.id])
        res = self.client.get(url)

        serializer = ActorSerializer(actor)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)