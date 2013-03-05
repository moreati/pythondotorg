from django.test import TestCase

from .. import admin     # coverage FTW
from ..models import Calendar, Event, OccurringRule, RecurringRule

from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime


class EventsModelsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='username', password='password')
        self.calendar = Calendar.objects.create(creator=self.user)
        self.event = Event.objects.create(creator=self.user, calendar=self.calendar)

    def test_occurring_event(self):
        now = timezone.now()

        occurring_time_dtstart = now + datetime.timedelta(days=3)
        occurring_time_dtend = occurring_time_dtstart + datetime.timedelta(days=5)

        ot = OccurringRule.objects.create(
            event=self.event,
            dt_start=occurring_time_dtstart,
            dt_end=occurring_time_dtend,
        )

        self.assertEqual(self.event.next_time.dt_start, occurring_time_dtstart)
        self.assertFalse(self.event.next_time.single_day)
        self.assertEqual(Event.objects.for_datetime().count(), 1)

        ot.dt_start = now - datetime.timedelta(days=5)
        ot.dt_end = now - datetime.timedelta(days=3)
        ot.save()

        event = Event.objects.get(pk=self.event.pk)
        self.assertEqual(event.next_time, None)
        self.assertEqual(Event.objects.for_datetime().count(), 0)

    def test_recurring_event(self):
        now = timezone.now()

        recurring_time_dtstart = now + datetime.timedelta(days=3)
        recurring_time_dtend = recurring_time_dtstart + datetime.timedelta(days=5)

        rt = RecurringRule.objects.create(
            event=self.event,
            begin=recurring_time_dtstart,
            finish=recurring_time_dtend,
        )
        self.assertEqual(Event.objects.for_datetime().count(), 1)
        self.assertEqual(self.event.next_time.dt_start, recurring_time_dtstart)

        rt.begin = now - datetime.timedelta(days=5)
        rt.finish = now - datetime.timedelta(days=3)
        rt.save()

        event = Event.objects.get(pk=self.event.pk)
        self.assertEqual(event.next_time, None)
        self.assertEqual(Event.objects.for_datetime().count(), 0)

    def test_event(self):
        now = timezone.now()

        occurring_time_dtstart = now + datetime.timedelta(days=5)
        occurring_time_dtend = occurring_time_dtstart + datetime.timedelta(days=6)

        ot = OccurringRule.objects.create(
            event=self.event,
            dt_start=occurring_time_dtstart,
            dt_end=occurring_time_dtend,
        )

        recurring_time_dtstart = now + datetime.timedelta(days=3)
        recurring_time_dtend = recurring_time_dtstart + datetime.timedelta(days=5)

        rt = RecurringRule.objects.create(
            event=self.event,
            begin=recurring_time_dtstart,
            finish=recurring_time_dtend,
        )
        self.assertEqual(Event.objects.for_datetime().count(), 1)
        self.assertEqual(self.event.next_time.dt_start, recurring_time_dtstart)

        rt.begin = now + datetime.timedelta(days=5)
        rt.finish = now + datetime.timedelta(days=3)
        rt.save()

        event = Event.objects.get(pk=self.event.pk)
        self.assertEqual(event.next_time.dt_start, ot.dt_start)
        self.assertEqual(Event.objects.for_datetime().count(), 1)
