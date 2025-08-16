from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from airport.models import (
    Airport,
    Route,
    Airplane,
    Flight,
    Order,
    AirplaneType,
    Crew, Ticket
)


User = get_user_model()


def sample_airport(**kwargs) -> Airport:
    defaults = {
        "name": "example_name",
        "closest_big_city": "example_city",
    }
    defaults.update(**kwargs)
    return Airport.objects.create(**defaults)


def sample_crew(**kwargs) -> Crew:
    defaults = {
        "first_name": "Andrii",
        "last_name": "Borysov",
        "position": Crew.Position.PILOT
    }
    defaults.update(**kwargs)
    return Crew.objects.create(**defaults)


def sample_route(**kwargs) -> Route:
    defaults = {
        "distance": 1000,
        "source": sample_airport(name="Boryspil"),
        "destination": sample_airport(name="Luton")
    }
    defaults.update(**kwargs)
    return Route.objects.create(**defaults)


def sample_airplane_type(**kwargs) -> AirplaneType:
    defaults = {
        "name": "example_name"
    }
    defaults.update(**kwargs)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**kwargs) -> Airplane:
    defaults = {
        "name": "Viktoria",
        "rows": 10,
        "seats_in_row": 10
    }
    defaults.update(**kwargs)
    return Airplane.objects.create(**defaults)


def sample_flight(**kwargs) -> Flight:
    defaults = {
        "departure_time": timezone.now(),
        "arrival_time": timezone.now() + timedelta(hours=2),
        "route": sample_route(),
        "airplane": sample_airplane()
    }
    defaults.update(**kwargs)
    return Flight.objects.create(**defaults)


def sample_user(**kwargs) -> User:
    defaults = {
        "email": "user@example.com",
        "password": "ytrewq123"
    }
    defaults.update(**kwargs)
    return User.objects.create_user(**defaults)


def sample_admin(**kwargs) -> User:
    defaults = {
        "email": "admin@example.com",
        "password": "ytrewq123"
    }
    defaults.update(**kwargs)
    return User.objects.create_superuser(**defaults)


def sample_order(user: User, **params) -> Order:
    defaults = {}
    defaults.update(params)
    return Order.objects.create(user=user, **defaults)


def sample_ticket(order: Order, **kwargs) -> Ticket:
    defaults = {
        "row": 1,
        "seat_in_row": 1,
        "order": order,
        "flight": sample_flight()
    }
    defaults.update(kwargs)
    return Ticket.objects.create(**defaults)
