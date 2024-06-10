from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from catalog.models import Genre, Actor, TheatreHall, Play
from catalog.serializers import (
    GenreSerializer,
    ActorSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PlayImageSerializer,
)


class GenreViewSet(GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class TheatreHallViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        if self.action == "image":
            return PlayImageSerializer
        return PlaySerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
