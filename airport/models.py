from datetime import timedelta, datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from airport.utils import create_custom_path
from airport_service import settings


class Airport(models.Model):
    """Model representing an airport."""
    name = models.CharField(max_length=100, db_index=True)
    closest_big_city = models.CharField(max_length=100)
    image = models.ImageField(null=True, upload_to=create_custom_path)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    """Model representing a flight route between two airports."""
    distance = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    source = models.ForeignKey(
        to=Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        to=Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )

    class Meta:
        ordering = ["distance"]
        unique_together = ("source", "destination")

    @property
    def full_route(self) -> str:
        return f"{self.source} -> {self.destination}"

    @staticmethod
    def validate_source_not_equals_destination(
        source: Airport,
        destination: Airport,
        error_to_raise: type[Exception]
    ) -> None:
        if source == destination:
            raise error_to_raise({
                "destination": "Destination can't be source"
            })

    def clean(self) -> None:
        super().clean()
        Route.validate_source_not_equals_destination(
            source=self.source,
            destination=self.destination,
            error_to_raise=ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.full_route


class AirplaneType(models.Model):
    """Model representing a type of airplane."""
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    """Model representing an airplane."""
    name = models.CharField(max_length=100, db_index=True)
    rows = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    seats_in_row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    airplane_type = models.ForeignKey(
        to=AirplaneType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="airplanes"
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.name} ({self.capacity} seats)"


class Crew(models.Model):
    """Model representing a crew member."""
    class Position(models.TextChoices):
        PILOT = ("pilot", "Pilot")
        ATTENDANT = ("attendant", "Flight Attendant")
        ENGINEER = ("engineer", "Engineer")

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(
        max_length=20,
        choices=Position.choices,
        default=Position.ATTENDANT
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        unique_together = ("first_name", "last_name")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class Flight(models.Model):
    """Model representing a flight with departure and arrival times."""
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    route = models.ForeignKey(
        to=Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        to=Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    crew = models.ManyToManyField(
        to=Crew,
        related_name="flights"
    )

    class Meta:
        ordering = ["departure_time", "arrival_time"]

    @property
    def duration(self) -> str:
        total_seconds = int(
            (self.arrival_time - self.departure_time)
            .total_seconds()
        )
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        hours_str = (
            f"{hours} hour"
            if hours == 1
            else f"{hours} hours"
        )
        minutes_str = (
            f"{minutes} minute"
            if minutes == 1
            else f"{minutes} minutes"
        )
        return f"{hours_str} {minutes_str}"

    @staticmethod
    def validate_min_arrival_time(
            arrival_time: datetime,
            departure_time: datetime,
            error_to_raise: type[Exception]
    ) -> None:
        if arrival_time <= departure_time + timedelta(minutes=30):
            raise error_to_raise({
                "arrival_time":
                    "Arrival time must be at least 30 minutes from departure time."
            })

    def clean(self) -> None:
        super().clean()
        Flight.validate_min_arrival_time(
            arrival_time=self.arrival_time,
            departure_time=self.departure_time,
            error_to_raise=ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{str(self.route)} at {self.departure_time.strftime('%Y-%m-%d %H:%M')}"
        )


class Order(models.Model):
    """Model representing a user's order for tickets."""
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Ticket(models.Model):
    """Model representing a ticket for a specific seat on a flight."""
    row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    seat_in_row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    flight = models.ForeignKey(
        to=Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        ordering = ["flight__departure_time"]
        unique_together = ("flight", "row", "seat_in_row")

    @staticmethod
    def validate_row_and_seat_within_capacity(
            row: int,
            airplane_rows: int,
            seat_in_row: int,
            airplane_seats_in_row: int,
            error_to_raise: type[Exception]
    ) -> None:
        errors = {}
        if row > airplane_rows:
            errors["row"] = f"Row must be in range 1 to {airplane_rows}"
        if seat_in_row > airplane_seats_in_row:
            errors["seat_in_row"] = f"Seat must be in range 1 to {airplane_seats_in_row}"
        if errors:
            raise error_to_raise(errors)

    def clean(self) -> None:
        super().clean()
        Ticket.validate_row_and_seat_within_capacity(
            row=self.row,
            airplane_rows=self.flight.airplane.rows,
            seat_in_row=self.seat_in_row,
            airplane_seats_in_row=self.flight.airplane.seats_in_row,
            error_to_raise=ValidationError
        )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Ticket for {str(self.flight)} "
            f"at row {self.row}, seat {self.seat_in_row}"
        )
