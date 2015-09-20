import datetime
from django.utils import timezone
from django.db import models
from projects.models import *
from management.tracdb import *

        
class StrongPoint(models.Model):
    retrospective = models.ForeignKey('SprintRetrospective')
    text = models.CharField(max_length=200)
    def __unicode__(self):
        return self.text    
    
class ShouldBeImproved(models.Model):
    retrospective = models.ForeignKey('SprintRetrospective')
    owner = models.ForeignKey('Session')
    text = models.CharField(max_length=200)        
    def __unicode__(self):
        return self.text   
        
class SprintRetrospective(models.Model):
    date =  models.DateField()
    def __unicode__(self):
        return "Sprint Retropective #" +  str(self.id) 

        

        
class SprintPlanning(models.Model):
    objective = models.TextField(blank=True)
    members = models.ManyToManyField('Session')
    startDate =  models.DateField()
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
        
        
class Ticket(models.Model):
    title = models.CharField(max_length=200)

