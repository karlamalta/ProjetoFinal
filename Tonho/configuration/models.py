from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class BindingTime(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'Feature binding time Item'
        verbose_name_plural = 'Feature binding times'  
        
    def __unicode__(self):
        return self.name
       
       