from django.contrib import admin
from management.models import *
from django.forms import *
from django.db import models
from django.db.models import Q
from assets.models import Feature
from admin_bootstrapped.admin.models import SortableInline

import time


class StrongPointsAdminInline(admin.TabularInline):
    model = StrongPoint
    verbose_name_plural = 'Strong points'
    verbose_name = 'Strong point'
    extra = 0


class ShouldBeImprovedAdminInline(admin.TabularInline):
    model = ShouldBeImproved
    verbose_name_plural = 'Should be improved'
    verbose_name = 'Should be improved'
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40, 'class': 'vLargeTextField', })},
    }


class StrongPointAdmin(admin.ModelAdmin):
    fields = ['text']

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


class SprintRetrospectiveAdmin(admin.ModelAdmin):
    fields = ['date', 'milestone']
    inlines = [StrongPointsAdminInline, ShouldBeImprovedAdminInline]


class SprintPlanningTicketsAdminInline(admin.TabularInline):
    model = SprintPlanningTickts
    verbose_name_plural = 'Tickets'
    verbose_name = 'Ticket'
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ticket":
            kwargs["queryset"] = Ticket.objects.filter(~Q(status="closed"))
            return db_field.formfield(**kwargs)
        return super(SprintPlanningTicketsAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SprintPlanningAdmin(admin.ModelAdmin):
    fields = ['objective', 'members', 'start_date', 'deadline', 'milestone']
    inlines = [SprintPlanningTicketsAdminInline]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40, 'class': 'vLargeTextField', })},
    }
    filter_horizontal = ("members",)


class FeatureRankScopeBacklogAdminInline(admin.StackedInline, SortableInline):
    model = ScopeBacklogFeatureRank
    verbose_name_plural = 'Features rank'
    verbose_name = 'Features rank'
    #fk_name = 'scopeBacklog'
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "feature":
            kwargs["queryset"] = Feature.objects.filter(type="concrete")
            return db_field.formfield(**kwargs)
        return super(FeatureRankScopeBacklogAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ScopeBacklogAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [FeatureRankScopeBacklogAdminInline]


def sqltodict(query):
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute(query)
    result = []
    for row in cursor.fetchall():
        rowset = []
        rowset.append(row[0])
        rowset.append(row[0])
        result.append(rowset)
    return result


def get_features():
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute("select id,name from assets_feature")
    result = []
    for row in cursor.fetchall():
        rowset = []
        rowset.append(row[0])
        rowset.append("#" + str(row[0]) + " " + str(row[1]))
        result.append(rowset)
    return result


class TicketAdminForm(ModelForm):
    summary = TextInput()
    types = sqltodict("select name from enum where type = 'ticket_type'")
    type = ChoiceField(choices=types)
    priorities = sqltodict("select name from enum where type = 'priority'")
    priority = ChoiceField(choices=priorities)
    versions = sqltodict("select name from version")
    version = ChoiceField(choices=versions)
    milestones = sqltodict("select name from milestone")
    milestone = ChoiceField(choices=milestones)
    owners = sqltodict("select sid from session")
    owner = ChoiceField(choices=owners)
    components = sqltodict("select name from component")
    component = ChoiceField(choices=components)

    related_features = get_features()
    related_feature = ChoiceField(required=False, choices=related_features)

    def __init__(self, *args, **kwargs):
        super(TicketAdminForm, self).__init__(*args, **kwargs)  # Call to ModelForm constructor
        self.fields['summary'].widget.attrs['rows'] = 1
        self.fields['description'].widget.attrs['rows'] = 4

        from django.db import connection

        cursor = connection.cursor()
        if self.instance.id:
            cursor.execute("select value from ticket_custom where ticket = " + str(self.instance.id))
            row = cursor.fetchone()
            if row is not None:
                self.fields['related_feature'].initial = row[0]

    class Meta:
        model = Ticket


class TicketAdmin(admin.ModelAdmin):
    fields = ['summary', 'description', 'type', 'component', 'priority', 'version', 'milestone', 'owner',
              'related_feature']
    form = TicketAdminForm
    #formfield_overrides = {
    #    models.TextField: {'widget': Textarea(attrs={'rows':2, #'cols':40,'class':'vLargeTextField',})},
    #}

    def save_model(self, request, obj, form, change):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute("INSERT OR REPLACE INTO ticket_custom VALUES (%s, %s, %s)", (obj.id, 'ticketref',
                                                                                    form.cleaned_data[
                                                                                        'related_feature']))
        epoch_time = str(int(time.time() * 1000000))
        obj.time = epoch_time
        obj.changetime = epoch_time
        obj.save()


admin.site.register(Ticket, TicketAdmin)
admin.site.register(StrongPoint, StrongPointAdmin)
admin.site.register(SprintRetrospective, SprintRetrospectiveAdmin)
admin.site.register(SprintPlanning, SprintPlanningAdmin)
admin.site.register(ScopeBacklog, ScopeBacklogAdmin)