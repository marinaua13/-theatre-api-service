import os
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class Actor(models.Model):
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name


def play_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class Play(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField()
    actors = models.ManyToManyField(Actor, related_name="plays")
    genres = models.ManyToManyField(Genre, related_name="plays")
    image = models.ImageField(null=True, upload_to=play_image_file_path)

    def __str__(self):
        return self.title


class TheatreHall(models.Model):
    name = models.CharField(max_length=70)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return f"{self.play.title} at {self.theatre_hall.name} on {self.show_time}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self):
        return f"Ticket:{self.id}. Row: {self.row}. Seat: {self.seat}. Performance: {self.performance}"
