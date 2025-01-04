from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class Route(models.Model):
    source = models.ForeignKey(
        "Station",
        on_delete=models.CASCADE,
        related_name="source_routes",
    )
    destination = models.ForeignKey(
        "Station",
        on_delete=models.CASCADE,
        related_name="destination_routes",
    )
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


class TrainType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        "TrainType",
        on_delete=models.CASCADE,
        related_name="trains",
    )

    @property
    def capacity(self):
        return self.places_in_cargo * self.cargo_num

    def __str__(self):
        return f"Train: {self.name}. Type: {self.train_type}"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Trip(models.Model):
    route = models.ForeignKey(
        "Route",
        on_delete=models.CASCADE,
        related_name="trips",
    )
    train = models.ForeignKey(
        "Train",
        on_delete=models.CASCADE,
        related_name="trips",
    )
    departure_time = models.DateTimeField(default=timezone.now)
    arrival_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Trip {self.route}. Train: {self.train.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    class Meta:
        unique_together = ("trip", "cargo", "seat")
        ordering = ["cargo", "seat"]

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.trip.train,
            ValidationError
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.trip} - (cargo: {self.cargo}, seat: {self.seat}"
