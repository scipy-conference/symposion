import csv
from datetime import datetime
from optparse import make_option
import os
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from symposion.conference.models import Section
from symposion.reviews.models import promote_proposal
from symposion.schedule.models import Day, Room, Schedule, Slot, SlotKind, SlotRoom
from symposion.proposals.models import ProposalBase

"""

presentations example

section_slug,date,time_start,time_end,kind,room,proposal_id,description
talks-posters,7/8/2014,14:45,15:00,Scientific Computing in Education,Grand Ballroom,185,
talks-posters,7/10/2014,12:15,13:30,Lunch,Room 203,,

rooms example

section_slug,name,order
talks-posters,Grand Ballroom,0
talks-posters,Room 203,1
talks-posters,Room 204,2
tutorials,Room 101,0
tutorials,Room 102,1

slotkinds example

section_slug,slot_kind,presentation_menu
talks-posters,Astronomy and Astrophysics Symposium,1
talks-posters,Bioinformatics Symposium,1
talks-posters,Break,0

"""

def create_presentation_slots(data):
    """ Creates a SlotRoom based on a csv file

    Room and SlotKind must exist
    If Day does not exist it will be created
    """

    for row in data:
        print row
        section_slug, date, start, end, kind_label, room_name, proposal_id, description = parse_presentation(row)
        schedule = get_schedule(row['section_slug'])

        room = Room.objects.get(schedule=schedule, name=room_name)
        slotkind = SlotKind.objects.get(schedule=schedule, label=kind_label)
        day, create = Day.objects.get_or_create(schedule=schedule, date=date)

        slot = Slot.objects.create(
            kind=slotkind,
            day=day,
            start=start,
            end=end,
        )
        SlotRoom.objects.create(slot=slot, room=room)

        if description != '':
            slot.content_override = description

        if proposal_id:
            assign_presentation(slot, schedule.section, proposal_id)


def assign_presentation(slot, section, proposal_id):
    try:
        proposal = ProposalBase.objects.get(pk=proposal_id)
    except ProposalBase.DoesNotExist:
        print 'No proposal found with pk %s, skipping' % proposal_id
        return
    presentation = promote_proposal(proposal)
    presentation.slot = slot
    presentation.section = section
    presentation.save()
    print 'assigning presentation for %s' % proposal_id
    slot.assign(presentation)


def create_rooms(data):
    for row in data:
        print row
        schedule = get_schedule(row['section_slug'])
        Room.objects.create(
            schedule = schedule,
            name=row['name'],
            order=row['order'],
        )


def create_slot_kinds(data):
    for row in data:
        print row
        schedule = get_schedule(row['section_slug'])
        presentation = row.get('presentation_menu', 0) == '1'
        SlotKind.objects.create(
            schedule=schedule,
            label=row['slot_kind'],
            presentation=presentation
        )

def parse_presentation(row):
    """ parses row from presentation csv file  
    """
    # section_slug,date,time_start,time_end,kind,room,proposal_id,description
    date = datetime.strptime(row['date'], "%m/%d/%Y")
    start = get_time(row['time_start'])
    end = get_time(row['time_end'])
    return row['section_slug'], date, start, end, row['kind'], row['room'], row.get('proposal_id', ''), row.get('description', '')


def get_time(timestring):
    time_obj = time.strptime(timestring, '%H:%M')
    time_obj = datetime(100, 1, 1, time_obj.tm_hour, time_obj.tm_min, 00)
    return time_obj.time()


def get_csv_data(csvfile):
    with open(csvfile) as fh:
        reader = csv.DictReader(fh)
        return [dict((k.strip(), v.strip()) for k, v in x.items()) for x in reader]


def get_schedule(section_slug):
    """ get Schedule for section
    """
    section = Section.objects.get(slug=section_slug)
    return Schedule.objects.get(section=section)


class Command(BaseCommand):
    args = 'csvfile'
    help = """
    Create a schedule grid for a conference section.

    In order for this to work a Schedule and associated Days must already exist.
    This code is sloppy. It was expendient. Backup everything before doing anything.

    presentations.csv example
    
    section_slug,date,time_start,time_end,kind,room,proposal_id,description
    talks-posters,7/8/2014,14:45,15:00,Scientific Computing in Education,Grand Ballroom,185,
    talks-posters,7/10/2014,12:15,13:30,Lunch,Room 203,,
    
    rooms.csv example
    
    section_slug,name,order
    talks-posters,Grand Ballroom,0
    talks-posters,Room 203,1
    talks-posters,Room 204,2
    tutorials,Room 101,0
    tutorials,Room 102,1
    
    slotkinds.csv example
    
    section_slug,slot_kind,presentation_menu
    talks-posters,Astronomy and Astrophysics Symposium,TRUE
    talks-posters,Bioinformatics Symposium,TRUE
    talks-posters,Break,FALSE

    """

    modeltypes = ['presentations', 'rooms', 'slotkinds']
    option_list = BaseCommand.option_list + (
        make_option(
            '-m',
            '--modeltype',
            dest='modeltype',
            type='choice',
            choices=modeltypes,
            action='store',
            default='presentations',
            metavar='MODEL_TYPE',
            help='Create objects of this model type. Valid types: %s' % modeltypes,
        ),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        assert os.path.isfile(args[0]), 'not a file: %s' % args[0]

        data = get_csv_data(args[0])

        if options['modeltype'] == 'presentations':
            create_presentation_slots(data)
        elif options['modeltype'] == 'rooms':
            create_rooms(data)
        elif options['modeltype'] == 'slotkinds':
            create_slot_kinds(data)
