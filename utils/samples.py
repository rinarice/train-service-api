import datetime

from django.contrib.auth import get_user_model

from train_service.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew, Trip, Order, Ticket
)


def sample_station(**params):
    defaults = {
        "name": "Test Station",
        "latitude": 12.34,
        "longitude": 10.12,
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_user(**params):
    defaults = {
        "email": "test@test.test",
        "password": "password",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_superuser(**params):
    defaults = {
        "email": "admin@test.test",
        "password": "password",
    }
    defaults.update(params)
    return get_user_model().objects.create_superuser(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_station(name="Source Station"),
        "destination": sample_station(name="Destination Station"),
        "distance": 100,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_train_type(**params):
    defaults = {
        "name": "Test Train Type",
    }
    defaults.update(params)
    return TrainType.objects.create(**defaults)


def sample_train(**params):
    train_type = sample_train_type()
    defaults = {
        "name": "Test Train",
        "cargo_num": 10,
        "places_in_cargo": 20,
        "train_type": train_type,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": "Test",
        "last_name": "Crew",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_trip(**params):
    route = sample_route()
    train = sample_train()

    defaults = {
        "route": route,
        "train": train,
        "departure_time": datetime.datetime(
            2025, 1, 10, 11, 30
        ),
        "arrival_time": datetime.datetime(
            2025, 1, 10, 15, 30
        ),
    }
    defaults.update(params)

    return Trip.objects.create(**defaults)


def sample_order(**params):
    if not params.get("user"):
        user = sample_user()
    else:
        user = params.get("user")

    defaults = {"user": user}
    defaults.update(params)

    return Order.objects.create(**defaults)


def sample_ticket(**params):
    trip = params.get("trip", sample_trip())
    if not params.get("order"):
        order = sample_order()
    else:
        order = params.get("order")

    defaults = {
        "cargo": 1,
        "seat": 1,
        "trip": trip,
        "order": order,
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)
