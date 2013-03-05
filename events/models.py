from operator import itemgetter

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from cms.models import ContentManageable, NameSlugModel
from timedelta.fields import TimedeltaField


# Create your models here.
class Calendar(ContentManageable):
    name = models.CharField(max_length=100)


class EventCategory(NameSlugModel):
    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('events:eventlist_category', kwargs={'slug': self.slug})


class EventLocation(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(blank=True, null=True, max_length=255)
    url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('events:eventlist_location', kwargs={'pk': self.pk})


class EventManager(models.Manager):
    def for_datetime(self, dt=None):
        if dt is None:
            dt = timezone.now()
        return self.filter(Q(occurring_rule__dt_start__gt=dt) | Q(recurring_rules__finish__gt=dt))


class Event(ContentManageable):
    title = models.CharField(max_length=200)
    calendar = models.ForeignKey(Calendar, related_name='events')

    description = models.TextField()
    venue = models.ForeignKey(EventLocation, null=True, blank=True, related_name='events')

    categories = models.ManyToManyField(EventCategory, related_name='events', blank=True, null=True)
    featured = models.BooleanField(default=False, db_index=True)

    objects = EventManager()

    def get_absolute_url(self):
        reverse('events:event_detail', kwargs={'pk': self.pk})

    @cached_property
    def next_time(self):
        now = timezone.now()
        recurring_start = occurring_start = None

        try:
            occurring_rule = self.occurring_rule
        except OccurringRule.DoesNotExist:
            pass
        else:
            if occurring_rule.dt_start > now:
                occurring_start = (occurring_rule.dt_start, occurring_rule)

        rrules = self.recurring_rules.filter(Q(finish__gt=now) | Q(finish__isnull=True))
        recurring_starts = [(rrule.dt_start, rrule) for rrule in rrules]
        recurring_starts.sort(key=itemgetter(0))

        try:
            recurring_start = recurring_starts[0]
        except IndexError:
            pass

        starts = [i for i in (recurring_start, occurring_start) if i is not None]
        starts.sort(key=itemgetter(0))
        try:
            return starts[0][1]
        except IndexError:
            return None


class OccurringRule(models.Model):
    event = models.OneToOneField(Event, related_name='occurring_rule')
    dt_start = models.DateTimeField(default=timezone.now)
    dt_end = models.DateTimeField(default=timezone.now)

    @property
    def begin(self):
        return self.dt_start

    @property
    def finish(self):
        return self.dt_end

    @property
    def duration(self):
        return self.dt_end - self.dt_start

    @property
    def single_day(self):
        return self.dt_start.date() == self.dt_end.date()


class RecurringRule(models.Model):
    event = models.ForeignKey(Event, related_name='recurring_rules')
    begin = models.DateTimeField(default=timezone.now)
    finish = models.DateTimeField(default=timezone.now)
    duration = TimedeltaField(default='15 mins')
    interval = TimedeltaField(_("Repeat every"), default="1w")

    @property
    def dt_start(self):
        since = timezone.now()

        occurrence = self.begin
        while occurrence < since:
            occurrence += self.interval

        return occurrence

    @property
    def dt_end(self):
        return self.dt_start + self.duration

    @property
    def single_day(self):
        return self.dt_start.date() == self.dt_end.date()


class Alarm(ContentManageable):
    event = models.ForeignKey(Event)
    trigger = models.PositiveSmallIntegerField(_("hours before the event occurs"), default=24)

    @property
    def recipient(self):
        full_name = self.creator.get_full_name()
        if full_name:
            return "%s <%s>" % (full_name, self.creator.email)
        return self.creator.email
