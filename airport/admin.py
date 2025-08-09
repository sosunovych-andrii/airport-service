from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    Airplane,
    Flight,
    Crew,
    Route,
    Ticket,
    Order,
    Airport,
    AirplaneType
)


admin.site.unregister(Group)

admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Ticket)
admin.site.register(Order)
admin.site.register(Airport)
admin.site.register(AirplaneType)
