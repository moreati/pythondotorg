from django.contrib import admin
from cms.admin import ContentManageableModelAdmin

from .models import Calendar, EventCategory, Event, OccurringTime, RecurringTime, Alarm


class EventInline(admin.StackedInline):
    model = Event


class CalendarAdmin(ContentManageableModelAdmin):
    inlines = [EventInline]


class OccurringTimeInline(admin.StackedInline):
    model = OccurringTime


class RecurringTimeInline(admin.StackedInline):
    model = RecurringTime


class AlarmInline(admin.StackedInline):
    model = Alarm


class EventAdmin(ContentManageableModelAdmin):
    inlines = [OccurringTimeInline, RecurringTimeInline, AlarmInline]


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(EventCategory, ContentManageableModelAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(OccurringTime)
admin.site.register(RecurringTime)
admin.site.register(Alarm, ContentManageableModelAdmin)
