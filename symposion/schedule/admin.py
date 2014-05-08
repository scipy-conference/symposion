from django.contrib import admin

from symposion.schedule.models import Schedule, Day, Room, SlotKind, Slot, SlotRoom, Presentation


admin.site.register(Schedule)
admin.site.register(
    Day,
    list_display=("date", "schedule"),
    list_filter=("schedule"),
)
admin.site.register(
    Room,
    list_display=("name", "order", "schedule")
)
admin.site.register(SlotKind)
admin.site.register(
    Slot,
    list_display=("day", "start", "end", "kind")
)
admin.site.register(
    SlotRoom,
    list_display=("slot", "room")
)
admin.site.register(
    Presentation,
    list_filter=("section", "slot", "cancelled")
)
