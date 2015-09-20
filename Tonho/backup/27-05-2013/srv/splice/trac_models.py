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
    id = models.TextField(blank=True)
    filename = models.TextField(blank=True)
    size = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    author = models.TextField(blank=True)
    ipnr = models.TextField(blank=True)
    class Meta:
        db_table = 'attachment'

class AuthCookie(models.Model):
    cookie = models.TextField(blank=True)
    name = models.TextField(blank=True)
    ipnr = models.TextField(blank=True)
    time = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'auth_cookie'

class Cache(models.Model):
    id = models.IntegerField(null=True, primary_key=True, blank=True)
    generation = models.IntegerField(null=True, blank=True)
    key = models.TextField(blank=True)
    class Meta:
        db_table = 'cache'

class Component(models.Model):
    name = models.TextField(unique=True, blank=True)
    owner = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'component'

class Enum(models.Model):
    type = models.TextField(blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'enum'

class Milestone(models.Model):
    name = models.TextField(unique=True, blank=True)
    due = models.IntegerField(null=True, blank=True)
    completed = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'milestone'

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

class Permission(models.Model):
    username = models.TextField(blank=True)
    action = models.TextField(blank=True)
    class Meta:
        db_table = 'permission'

class Report(models.Model):
    id = models.IntegerField(null=True, primary_key=True, blank=True)
    author = models.TextField(blank=True)
    title = models.TextField(blank=True)
    query = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'report'

class Repository(models.Model):
    id = models.IntegerField(null=True, blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'repository'

class Revision(models.Model):
    repos = models.IntegerField(null=True, blank=True)
    rev = models.TextField(blank=True)
    time = models.IntegerField(null=True, blank=True)
    author = models.TextField(blank=True)
    message = models.TextField(blank=True)
    class Meta:
        db_table = 'revision'

class Session(models.Model):
    sid = models.TextField(blank=True)
    authenticated = models.IntegerField(null=True, blank=True)
    last_visit = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'session'

class SessionAttribute(models.Model):
    sid = models.TextField(blank=True)
    authenticated = models.IntegerField(null=True, blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'session_attribute'

class System(models.Model):
    name = models.TextField(unique=True, blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'system'

class Ticket(models.Model):
    id = models.IntegerField(null=True, primary_key=True, blank=True)
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
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    class Meta:
        db_table = 'ticket'

class TicketChange(models.Model):
    ticket = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    author = models.TextField(blank=True)
    field = models.TextField(blank=True)
    oldvalue = models.TextField(blank=True)
    newvalue = models.TextField(blank=True)
    class Meta:
        db_table = 'ticket_change'

class TicketCustom(models.Model):
    ticket = models.IntegerField(null=True, blank=True)
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = 'ticket_custom'

class Version(models.Model):
    name = models.TextField(unique=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'version'

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

