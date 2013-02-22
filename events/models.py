from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cms.models import ContentManageable
from timedelta.fields import TimedeltaField


# Create your models here.
class Calendar(ContentManageable):
    name = models.CharField(max_length=100)


class EventCategory(ContentManageable):
    name = models.CharField(max_length=100)
    slug = models.SlugField()


class Event(ContentManageable):
    calendar = models.ForeignKey(Calendar, related_name='events')

    description = models.TextField()
    location = models.CharField(blank=True, null=True, max_length=255)
    url = models.URLField(blank=True, null=True)

    categories = models.ManyToManyField(EventCategory, related_name='events', blank=True, null=True)

    def get_next_datetime(self):
        now = timezone.now()
        try:
            occurring_time = self.occurring_time
        except OccurringTime.DoesNotExist:
            pass
        else:
            if occurring_time.dt_start > now:
                return occurring_time.dt_start

        try:
            times = self.recurring_times.filter(Q(dt_end__gt=now) | Q(dt_end__isnull=True))
            starts = [time.next_dt_start(now) for time in times]
            return min(starts)

        except IndexError:
            return None


class EventTime(models.Model):
    dt_start = models.DateTimeField(default=timezone.now)
    dt_end = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class OccurringTime(EventTime):
    event = models.OneToOneField(Event, related_name='occurring_time')

    @property
    def duration(self):
        return self.dt_end - self.dt_start


class RecurringTime(EventTime):
    event = models.ForeignKey(Event, related_name='recurring_times')
    duration = TimedeltaField(default='15 mins')
    interval = TimedeltaField(_("Repeat every"), default="1w")

    def next_dt_start(self, since):
        occurrence = self.dt_start
        while occurrence < since:
            occurrence += self.interval

        return occurrence


class Alarm(ContentManageable):
    event = models.ForeignKey(Event)
    trigger = models.PositiveSmallIntegerField(_("hours before the event occurs"), default=24)

    @property
    def recipient(self):
        full_name = self.creator.get_full_name()
        if full_name:
            return "%s <%s>" % (full_name, self.creator.email)
        return self.creator.email
