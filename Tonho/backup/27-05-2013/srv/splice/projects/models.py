from django.db import models
from management.models import *
from management.tracdb import Session

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    configuration = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name
    
class FeatureVariabilityType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
  
    def __unicode__(self):
        return self.name

class FeatureType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
  
    def __unicode__(self):
        return self.name
        
class BindingTime(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
        
class Feature(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    configuration = models.CharField(max_length=200)  
    
    variability = models.ForeignKey(FeatureVariabilityType)
    type = models.ForeignKey(FeatureType)
    bindingTime = models.ForeignKey(BindingTime)

    father = models.ForeignKey('self', blank=True, null=True)
    requires = models.ManyToManyField("self", blank=True, symmetrical=False, 
                                      related_name='requires_features')
    excludes = models.ManyToManyField("self", blank=True, symmetrical=False, 
                                      related_name='excludes_features')
                                      
    glossary = models.ManyToManyField('Glossary', blank=True)
    def __unicode__(self):
        return "#" + str(self.id) + " "  + self.name
    
class ProductMap(models.Model):
    name = models.CharField(max_length=200)
    features = models.ManyToManyField(Feature, blank=True, symmetrical=False, 
                                      related_name='features_productmaps')
    def __unicode__(self):
        return "Product: " + self.product.name + " product map."
        
class Glossary(models.Model):        
    term = models.CharField(max_length=200)
    definition = models.TextField(max_length=200)        
 
    class Meta:
        verbose_name = 'Glossary Item'
        verbose_name_plural = 'Glossary' 
    def __unicode__(self):
        return self.term    
    


class ScopeBacklog(models.Model):  
    name = models.CharField(max_length=200)
    feature_rank = models.ManyToManyField('ScopeBacklogFeatureRank')
    def __unicode__(self):
        return self.name + " backlog"
    
class ScopeBacklogFeatureRank(models.Model): 
    scopeBacklog = models.ForeignKey(ScopeBacklog)
    feature = models.ForeignKey(Feature)
    ranking = models.CharField(max_length=200)
    
class Scenario(models.Model):        
    description = models.TextField(blank=True)
    owners = models.ManyToManyField(Session)
    features = models.ManyToManyField('Feature')
    
    dependencies = models.ManyToManyField("self", blank=True, symmetrical=False, 
                                      related_name='dependencies_scenario')
    def __unicode__(self):
        return self.description                                        
    
class FunctionalSpecification(models.Model):    

    title = models.CharField(max_length=200)
    rationale = models.TextField(blank=True)
    precondition = models.TextField(blank=True)
    owner = models.ManyToManyField(Session)
    scenarios = models.ManyToManyField('Scenario')
    feature = models.ForeignKey(Feature)
    
    
    mainSteps = models.ManyToManyField('MainSteps', blank=True, symmetrical=False, 
                                      related_name='mainsteps_funcspec')
    alternativeSteps = models.ManyToManyField('AlternativeSteps', blank=True, symmetrical=False, related_name='alternativesteps_funcspec')
    exceptionSteps = models.ManyToManyField('ExceptionSteps', blank=True, symmetrical=False, related_name='exceptionsteps_funcspec')

    def __unicode__(self):
        return self.title  
        
class MainSteps(models.Model):    
    functionalSpecification = models.ForeignKey(FunctionalSpecification)
    userAction = models.CharField(max_length=200)
    systemResponse = models.CharField(max_length=200)

class AlternativeSteps(models.Model):    
    functionalSpecification = models.ForeignKey(FunctionalSpecification)
    userAction = models.CharField(max_length=200)
    systemResponse = models.CharField(max_length=200)

class ExceptionSteps(models.Model):    
    functionalSpecification = models.ForeignKey(FunctionalSpecification)
    userAction = models.CharField(max_length=200)
    systemResponse = models.CharField(max_length=200)

STATUS_CHOICES = (('pass', 'Passed'),
                    ('failed', 'Failed'))
class TestExecution(models.Model):    
    functionalSpecification = models.ForeignKey(FunctionalSpecification)
    result = models.CharField(max_length=20, choices=STATUS_CHOICES)
    def __unicode__(self):
        return "Test execution" + str(self.id)  
    