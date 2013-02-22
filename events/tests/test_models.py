#from freezegun import freeze_time
from django.test import TestCase

from .. import admin     # coverage FTW
from ..models import Calendar, Event, OccurringTime, RecurringTime

from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
import pytz


class EventsModelsTests(TestCase):
    def setUp(self):
        pass
        self.user = get_user_model().objects.create_user(username='username', password='password')
        self.calendar = Calendar.objects.create(creator=self.user)

    # TODO: freezegun doesn't play well with Django 1.5 Find a way to freeze time
    #@freeze_time("2013-01-01 13:00:00", tz_offset=0)
    def test_recurring_event(self):
        # this event occurs on jan 3rd, and every Wednesday since the 2nd.
        # It always start at 14:00 UTC and lasts 3 hours.
        # Note that the first occurrence of the recurring time will happen one
        # day earlier than the occurring time (jan 3rd).

        event = Event.objects.create(creator=self.user)

        time = timezone.make_aware(datetime.time(14, 0), pytz.utc)
        day = datetime.date(2013, 1, 1) + datetime.timedelta(days=2)
        wednesday = datetime.date(2013, 1, 2)

        occurring_time_dtstart = datetime.datetime.combine(day, time)
        occurring_time_dtend = occurring_time_dtstart + datetime.timedelta(hours=3)

        recurring_time_dtstart = datetime.datetime.combine(wednesday, time)
        recurring_time_dtstart = datetime.datetime.combine(wednesday, time)

        OccurringTime.objects.create(
            event=event,
            dt_start=occurring_time_dtstart,
            dt_end=occurring_time_dtend,
        )

        RecurringTime.objects.create(
            event=event,
            dt_start=recurring_time_dtstart,
            duration=datetime.timedelta(hours=3),
            interval=7,
        )

        self.assertEqual(event.get_next_datetime(), datetime(2013, 1, 2, 14, 00, tzinfo=pytz.utc))
