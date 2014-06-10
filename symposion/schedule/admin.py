from django.contrib import admin

from symposion.schedule.models import Schedule, Day, Room, SlotKind, Slot, SlotRoom, Presentation


admin.site.register(Schedule)
admin.site.register(
    Day,
    #list_display=("date", "schedule")
    # TODO this line displays useful information but intermittently causes: FieldDoesNotExist: Day has no field named 's'
)
admin.site.register(
    Room,
    list_display=("name", "order", "schedule"),
    list_filter=("schedule")
)
admin.site.register(
    SlotKind,
    list_display=("label", "schedule", "presentation"),
    list_filter=("presentation")
)
admin.site.register(
    Slot,
    list_display=("day", "start", "end", "kind"),
    list_filter=("kind")
)
admin.site.register(
    SlotRoom,
    list_display=("room", "slot")
)
admin.site.register(
    Presentation,
    list_display=("title", "speaker", "section", "number"),
    list_filter=("section", "slot", "cancelled")
)
