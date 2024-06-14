from django.urls import path, include
from rest_framework import routers

from catalog.views import (
    GenreViewSet,
    ActorViewSet,
    TheatreHallViewSet,
    PlayViewSet,
    PerformanceViewSet,
    ReservationViewSet,
)

app_name = "catalog"

router = routers.DefaultRouter()
router.register("genres", GenreViewSet),
router.register("actors", ActorViewSet),
router.register("theatre_hall", TheatreHallViewSet),
router.register("play", PlayViewSet)
router.register("performance", PerformanceViewSet),
router.register("reservations", ReservationViewSet)
urlpatterns = [path("", include(router.urls))]
