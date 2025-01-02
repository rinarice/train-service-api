from django.contrib import admin
from train_service.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Trip,
    Ticket,
    Order,
)

admin.site.register(Station)
admin.site.register(Route)
admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Crew)
admin.site.register(Trip)
admin.site.register(Ticket)
admin.site.register(Order)
