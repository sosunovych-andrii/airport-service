from django.urls import path, include
from rest_framework import routers

from airport.views.airport import AirportViewSet
from airport.views.crew import CrewViewSet
from airport.views.flight import FlightViewSet
from airport.views.order import OrderViewSet
from airport.views.route import RouteViewSet
from airport.views.airplane import (
    AirplaneTypeViewSet,
    AirplaneViewSet
)


app_name = "airport"


router = routers.DefaultRouter()
router.register(
    prefix="airports",
    viewset=AirportViewSet,
    basename="airport"
)
router.register(
    prefix="routes",
    viewset=RouteViewSet,
    basename="route"
)
router.register(
    prefix="airplane_types",
    viewset=AirplaneTypeViewSet,
    basename="airplane_type"
)
router.register(
    prefix="airplanes",
    viewset=AirplaneViewSet,
    basename="airplane"
)
router.register(
    prefix="crews",
    viewset=CrewViewSet,
    basename="crew"
)
router.register(
    prefix="flights",
    viewset=FlightViewSet,
    basename="flight"
)
router.register(
    prefix="orders",
    viewset=OrderViewSet,
    basename="order"
)

urlpatterns = [
    path("", include(router.urls))
]
