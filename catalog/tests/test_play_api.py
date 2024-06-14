import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Play, Genre, Actor, TheatreHall, Performance
from catalog.serializers import PlayListSerializer, PlayDetailSerializer

PLAY_URL = reverse("catalog:play-list")
PERFORMANCE_URL = reverse("catalog:performance-list")


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
    }
    actors = params.pop("actors", None)
    genres = params.pop("genres", None)
    defaults.update(params)

    play = Play.objects.create(**defaults)

    if actors:
        play.actors.set(actors)
    if genres:
        play.genres.set(genres)

    return play


def sample_genre(**params):
    defaults = {
        "name": "Sample genre",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "test_name", "last_name": "test_last_name"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(name="Blue", rows=20, seats_in_row=20)

    defaults = {
        "show_time": "2024-06-02 14:00:00",
        "play": None,
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def image_upload_url(play_id):
    return reverse("catalog:play-upload-image", args=[play_id])


def detail_url(play_id):
    return reverse("catalog:play-detail", args=[play_id])


class PlayImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.play = sample_play()
        self.genre = sample_genre()
        self.actor = sample_actor()
        self.performance = sample_performance(play=self.play)

    def tearDown(self):
        self.play.image.delete()

    def test_upload_image_to_play(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.play.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.play.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.play.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_movie_list(self):
        url = PLAY_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "genres": [1],
                    "actors": [1],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(title="Title")
        self.assertFalse(play.image)


class UnauthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_movies_list(self):
        sample_play()
        res = self.client.get(PLAY_URL)
        movies = Play.objects.all()
        serializer = PlayListSerializer(movies, many=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_plays_list_with_actors_and_genres(self):
        sample_play()

        play_with_actor = sample_play(title="Giselle")
        actor = Actor.objects.create(first_name="Carlotta", last_name="Grisi")
        play_with_actor.actors.add(actor)

        play_with_genre = sample_play(title="Giselle")
        genre = Genre.objects.create(name="Ballet")
        play_with_genre.genres.add(genre)

        res = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_filter_plays_by_actors_and_genres_title(self):
        play_with_actor = sample_play(title="Giselle")
        play_with_genre = sample_play(title="Apollo")
        another_play = sample_play(title="Carmen")

        actor = Actor.objects.create(first_name="Carlotta", last_name="Grisi")
        genre = Genre.objects.create(name="Ballet")

        play_with_actor.actors.add(actor)
        play_with_genre.genres.add(genre)

        res = self.client.get(PLAY_URL, {"actors": actor.id})
        serializer = PlayListSerializer(
            Play.objects.filter(actors__id=actor.id).distinct(), many=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)
        self.assertNotIn(another_play.id, [play["id"] for play in res.data])

        res = self.client.get(PLAY_URL, {"genres": genre.id})
        serializer = PlayListSerializer(
            Play.objects.filter(genres__id=genre.id).distinct(), many=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

        res = self.client.get(PLAY_URL, {"title": "Apollo"})
        serializer = PlayListSerializer(
            Play.objects.filter(title__icontains="Apollo").distinct(), many=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

        res = self.client.get(
            PLAY_URL, {"actors": actor.id, "genres": genre.id, "title": "Apollo"}
        )
        serializer = PlayListSerializer(
            Play.objects.filter(
                actors__id=actor.id, genres__id=genre.id, title__icontains="Apollo"
            ).distinct(),
            many=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_play(self):
        play = sample_play()
        play.actors.add(Actor.objects.create(first_name="Carlotta", last_name="Grisi"))
        play.genres.add(Genre.objects.create(name="Ballet"))

        url = detail_url(play.id)

        res = self.client.get(url)
        serializer = PlayDetailSerializer(play)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = {
            "title": "Sample play",
            "description": "Sample description",
        }
        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="admin12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        actor = Actor.objects.create(first_name="John", last_name="Doe")
        genre = Genre.objects.create(name="Drama")
        payload = {
            "title": "Sample play",
            "description": "Sample description",
            "actors": [actor.id],
            "genres": [genre.id],
        }

        res = self.client.post(PLAY_URL, payload)
        print(res.data)  # For debugging
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(
            title=payload["title"],
            description=payload["description"],
        )

        self.assertIsNotNone(play)
        self.assertEqual(play.title, payload["title"])
        self.assertEqual(play.description, payload["description"])

    def test_create_play_with_genre(self):
        actor = Actor.objects.create(first_name="Carlotta", last_name="Grisi")
        genre = Genre.objects.create(name="Ballet")
        payload = {
            "title": "Sample play",
            "description": "Sample description",
            "actors": [actor.id],
            "genres": [genre.id],
        }
        res = self.client.post(PLAY_URL, payload)
        print(res.data)  # For debugging
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(actor.id, res.data["actors"])
        self.assertIn(genre.id, res.data["genres"])
