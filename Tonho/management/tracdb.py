# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Attachment(models.Model):
    type = models.TextField(blank=True)
    id = models.TextField(blank=True,primary_key=True)
    filename = models.TextField(blank=True)
    size = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    author = models.TextField(blank=True)
    ipnr = models.TextField(blank=True)
    class Meta:
        db_table = 'attachment'
        managed = False

class AuthCookie(models.Model):
    cookie = models.TextField(blank=True)
    name = models.TextField(blank=True)
    ipnr = models.TextField(blank=True)
    time = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'auth_cookie'
        managed = False

class Cache(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    generation = models.IntegerField(null=True, blank=True)
    key = models.TextField(blank=True)
    class Meta:
        db_table = 'cache'
        managed = False

class Component(models.Model):
    name = models.TextField(unique=True, blank=True)
    owner = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'component'
        managed = False

class Enum(models.Model):
    type = models.TextField(blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'enum'
        managed = True

class Milestone(models.Model):
    name = models.TextField(primary_key=True,unique=True)
    due = models.IntegerField(null=True, blank=True)
    completed = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'milestone'
        managed = False
    def __unicode__(self):
        return self.name   

class NodeChange(models.Model):
    repos = models.IntegerField(null=True, blank=True)
    rev = models.TextField(blank=True)
    path = models.TextField(blank=True)
    node_type = models.TextField(blank=True)
    change_type = models.TextField(blank=True)
    base_path = models.TextField(blank=True)
    base_rev = models.TextField(blank=True)
    class Meta:
        db_table = 'node_change'
        managed = False

class Permission(models.Model):
    username = models.TextField(blank=True)
    action = models.TextField(blank=True)
    class Meta:
        db_table = 'permission'
        managed = False

class Report(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    author = models.TextField(blank=True)
    title = models.TextField(blank=True)
    query = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'report'
        managed = False

class Repository(models.Model):
    id = models.IntegerField(primary_key=True,blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'repository'
        managed = False

class Revision(models.Model):
    repos = models.IntegerField(null=True, blank=True)
    rev = models.TextField(blank=True)
    time = models.IntegerField(null=True, blank=True)
    author = models.TextField(blank=True)
    message = models.TextField(blank=True)
    class Meta:
        db_table = 'revision'
        managed = False

class Session(models.Model):
    sid = models.TextField(blank=True, primary_key=True)
    authenticated = models.IntegerField(null=True, blank=True)
    last_visit = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'session'
        managed = False
    def __unicode__(self):
        return self.sid
        
class SessionAttribute(models.Model):
    sid = models.TextField(blank=True)
    authenticated = models.IntegerField(null=True, blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'session_attribute'
        managed = False

class System(models.Model):
    name = models.TextField(unique=True, blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'system'
        managed = False

class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    summary = models.TextField(blank=False)
    description = models.TextField(blank=False)
    type = models.TextField(blank=True)
    time = models.IntegerField(null=True, blank=True)
    changetime = models.IntegerField(null=True, blank=True)
    component = models.TextField(blank=True)
    severity = models.TextField(blank=True)
    priority = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    reporter = models.TextField(blank=True)
    cc = models.TextField(blank=True)
    version = models.TextField(blank=True)
    milestone = models.TextField(blank=True)
    status = models.TextField(blank=True)
    resolution = models.TextField(blank=True)

    keywords = models.TextField(blank=True)
    class Meta:
        db_table = 'ticket'
        managed = False
        
    def __unicode__(self):
        return "#" +  str(self.id) + " " + self.summary

class TicketChange(models.Model):
    ticket = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    author = models.TextField(blank=True)
    field = models.TextField(blank=True)
    oldvalue = models.TextField(blank=True)
    newvalue = models.TextField(blank=True)
    class Meta:
        db_table = 'ticket_change'
        managed = False

class TicketCustom(models.Model):
    ticket = models.IntegerField(null=True, blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'ticket_custom'
        managed = False

class Version(models.Model):
    name = models.TextField(unique=True,primary_key=True)
    time = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'version'
        managed = False
    def __unicode__(self):
        return self.name

class Wiki(models.Model):
    name = models.TextField(blank=True)
    version = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    author = models.TextField(blank=True)
    ipnr = models.TextField(blank=True)
    text = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    readonly = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'wiki'
        managed = False

