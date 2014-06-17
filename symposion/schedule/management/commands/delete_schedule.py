from django.core.management.base import BaseCommand
from django.db import transaction

from symposion.schedule import models


class Command(BaseCommand):
    help = """
    Delete schedule, but not Conference or Section
    """
    @transaction.commit_on_success
    def handle(self, *args, **options):
        models.SlotRoom.objects.all().delete()
        models.Presentation.objects.all().delete()
        models.Slot.objects.all().delete()
        models.SlotKind.objects.all().delete()
        models.Room.objects.all().delete()
        models.Day.objects.all().delete()
