from django.contrib import admin
from cms.admin import ContentManageableModelAdmin

from .models import Calendar, EventCategory, Event, OccurringRule, RecurringRule, Alarm


class EventInline(admin.StackedInline):
    model = Event


class CalendarAdmin(ContentManageableModelAdmin):
    inlines = [EventInline]


class OccurringRuleInline(admin.StackedInline):
    model = OccurringRule


class RecurringRuleInline(admin.StackedInline):
    model = RecurringRule


class AlarmInline(admin.StackedInline):
    model = Alarm


class EventAdmin(ContentManageableModelAdmin):
    inlines = [OccurringRuleInline, RecurringRuleInline, AlarmInline]


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(EventCategory, ContentManageableModelAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(OccurringRule)
admin.site.register(RecurringRule)
admin.site.register(Alarm, ContentManageableModelAdmin)
