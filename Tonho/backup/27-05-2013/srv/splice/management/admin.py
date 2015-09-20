from django.contrib import admin
from management.models import *

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
    
class StrongPointAdmin(admin.ModelAdmin):
    fields = ['text']
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}
    
class SprintRetrospectiveAdmin(admin.ModelAdmin):
    fields = ['date']
    inlines = [ StrongPointsAdminInline,ShouldBeImprovedAdminInline ]

class SprintPlanningTicketsAdminInline(admin.TabularInline):
    model = SprintPlanningTickts
    verbose_name_plural = 'Tickets'
    verbose_name = 'Ticket'
    extra = 0    

class SprintPlanningAdmin(admin.ModelAdmin):
    fields = ['objective','members','startDate','deadline',]
    inlines = [ SprintPlanningTicketsAdminInline ]



admin.site.register(StrongPoint, StrongPointAdmin)
admin.site.register(SprintRetrospective, SprintRetrospectiveAdmin)
admin.site.register(SprintPlanning, SprintPlanningAdmin)