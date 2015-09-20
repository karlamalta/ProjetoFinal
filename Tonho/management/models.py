import datetime
from django.utils import timezone
from django.db import models
from assets.models import *
from management.tracdb import *


class StrongPoint(models.Model):
    retrospective = models.ForeignKey('SprintRetrospective')
    text = models.CharField(max_length=200)

    def __unicode__(self):
        return self.text    


class ShouldBeImproved(models.Model):
    retrospective = models.ForeignKey('SprintRetrospective')
    owner = models.ManyToManyField('Session')
    text = models.TextField()

    def __unicode__(self):
        return self.text   


class SprintRetrospective(models.Model):
    date = models.DateField()
    milestone = models.ForeignKey(Milestone)

    def __unicode__(self):
        return "Sprint Retropective #" +  str(self.id) 


class SprintPlanning(models.Model):
    objective = models.TextField(blank=True)
    milestone = models.ForeignKey(Milestone)
    members = models.ManyToManyField('Session')
    start_date = models.DateField()
    deadline = models.DateField()
    tickets = models.ManyToManyField('Ticket')

    def __unicode__(self):
        return "Sprint Planning #" +  str(self.id) 


class SprintPlanningTickts(models.Model):
    sprintplanning = models.ForeignKey(SprintPlanning)
    ticket =  models.ForeignKey('Ticket')

    def __unicode__(self):
        return "Sprint Tickets #" +  str(self.id)    
    
    def __unicode__(self):
        return "Sprint #" +  str(self.id)


class ScopeBacklog(models.Model):  
    name = models.CharField(max_length=200)
    feature_rank = models.ManyToManyField('assets.Feature')

    def __unicode__(self):
        return self.name + " backlog"

    class Meta:
        verbose_name = 'Scope backlog Item'
        verbose_name_plural = 'Scope backlog' 
        
EFFORT_CHOICES = ((0, '0'),
                    (1, '1'),
                    (3, '3'),
                    (5, '5'),
                    (8, '8'),
                    (13, '13'),
                    (20, '20'),
                    (40, '40'),
                    (100, '100'))


class ScopeBacklogFeatureRank(models.Model): 
    scope_backlog = models.ForeignKey(ScopeBacklog)
    feature = models.ForeignKey('assets.Feature')
    position = models.PositiveSmallIntegerField("Position")    
    effort = models.PositiveSmallIntegerField(choices=EFFORT_CHOICES)

    def __unicode__(self):
        return self.feature

    class Meta:
        ordering = ('position', )
