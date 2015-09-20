# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Enum'
        db.create_table(u'enum', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'management', ['Enum'])

        # Adding model 'StrongPoint'
        db.create_table(u'management_strongpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('retrospective', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management.SprintRetrospective'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'management', ['StrongPoint'])

        # Adding model 'ShouldBeImproved'
        db.create_table(u'management_shouldbeimproved', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('retrospective', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management.SprintRetrospective'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'management', ['ShouldBeImproved'])

        # Adding M2M table for field owner on 'ShouldBeImproved'
        db.create_table(u'management_shouldbeimproved_owner', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shouldbeimproved', models.ForeignKey(orm[u'management.shouldbeimproved'], null=False)),
            ('session', models.ForeignKey(orm[u'management.session'], null=False))
        ))
        db.create_unique(u'management_shouldbeimproved_owner', ['shouldbeimproved_id', 'session_id'])

        # Adding model 'SprintRetrospective'
        db.create_table(u'management_sprintretrospective', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'management', ['SprintRetrospective'])

        # Adding model 'SprintPlanning'
        db.create_table(u'management_sprintplanning', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('objective', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('deadline', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'management', ['SprintPlanning'])

        # Adding M2M table for field members on 'SprintPlanning'
        db.create_table(u'management_sprintplanning_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sprintplanning', models.ForeignKey(orm[u'management.sprintplanning'], null=False)),
            ('session', models.ForeignKey(orm[u'management.session'], null=False))
        ))
        db.create_unique(u'management_sprintplanning_members', ['sprintplanning_id', 'session_id'])

        # Adding M2M table for field tickets on 'SprintPlanning'
        db.create_table(u'management_sprintplanning_tickets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sprintplanning', models.ForeignKey(orm[u'management.sprintplanning'], null=False)),
            ('ticket', models.ForeignKey(orm[u'management.ticket'], null=False))
        ))
        db.create_unique(u'management_sprintplanning_tickets', ['sprintplanning_id', 'ticket_id'])

        # Adding model 'SprintPlanningTickts'
        db.create_table(u'management_sprintplanningtickts', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sprintplanning', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management.SprintPlanning'])),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management.Ticket'])),
        ))
        db.send_create_signal(u'management', ['SprintPlanningTickts'])

        # Adding model 'ScopeBacklog'
        db.create_table(u'management_scopebacklog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'management', ['ScopeBacklog'])

        # Adding M2M table for field feature_rank on 'ScopeBacklog'
        db.create_table(u'management_scopebacklog_feature_rank', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scopebacklog', models.ForeignKey(orm[u'management.scopebacklog'], null=False)),
            ('scopebacklogfeaturerank', models.ForeignKey(orm[u'management.scopebacklogfeaturerank'], null=False))
        ))
        db.create_unique(u'management_scopebacklog_feature_rank', ['scopebacklog_id', 'scopebacklogfeaturerank_id'])

        # Adding model 'ScopeBacklogFeatureRank'
        db.create_table(u'management_scopebacklogfeaturerank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scope_backlog', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['management.ScopeBacklog'])),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Feature'])),
            ('ranking', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'management', ['ScopeBacklogFeatureRank'])


    def backwards(self, orm):
        # Deleting model 'Enum'
        db.delete_table(u'enum')

        # Deleting model 'StrongPoint'
        db.delete_table(u'management_strongpoint')

        # Deleting model 'ShouldBeImproved'
        db.delete_table(u'management_shouldbeimproved')

        # Removing M2M table for field owner on 'ShouldBeImproved'
        db.delete_table('management_shouldbeimproved_owner')

        # Deleting model 'SprintRetrospective'
        db.delete_table(u'management_sprintretrospective')

        # Deleting model 'SprintPlanning'
        db.delete_table(u'management_sprintplanning')

        # Removing M2M table for field members on 'SprintPlanning'
        db.delete_table('management_sprintplanning_members')

        # Removing M2M table for field tickets on 'SprintPlanning'
        db.delete_table('management_sprintplanning_tickets')

        # Deleting model 'SprintPlanningTickts'
        db.delete_table(u'management_sprintplanningtickts')

        # Deleting model 'ScopeBacklog'
        db.delete_table(u'management_scopebacklog')

        # Removing M2M table for field feature_rank on 'ScopeBacklog'
        db.delete_table('management_scopebacklog_feature_rank')

        # Deleting model 'ScopeBacklogFeatureRank'
        db.delete_table(u'management_scopebacklogfeaturerank')


    models = {
        u'assets.feature': {
            'Meta': {'object_name': 'Feature'},
            'binding_time': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['configuration.BindingTime']"}),
            'configuration': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'excludes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'excludes_features'", 'blank': 'True', 'to': u"orm['assets.Feature']"}),
            'glossary': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['assets.Glossary']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['assets.Feature']"}),
            'requires': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'requires_features'", 'blank': 'True', 'to': u"orm['assets.Feature']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'variability': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'assets.glossary': {
            'Meta': {'object_name': 'Glossary'},
            'definition': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'configuration.bindingtime': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BindingTime'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'management.attachment': {
            'Meta': {'object_name': 'Attachment', 'db_table': "u'attachment'", 'managed': 'False'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filename': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'ipnr': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.authcookie': {
            'Meta': {'object_name': 'AuthCookie', 'db_table': "u'auth_cookie'", 'managed': 'False'},
            'cookie': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipnr': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'management.cache': {
            'Meta': {'object_name': 'Cache', 'db_table': "u'cache'", 'managed': 'False'},
            'generation': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.component': {
            'Meta': {'object_name': 'Component', 'db_table': "u'component'", 'managed': 'False'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.enum': {
            'Meta': {'object_name': 'Enum', 'db_table': "u'enum'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.milestone': {
            'Meta': {'object_name': 'Milestone', 'db_table': "u'milestone'", 'managed': 'False'},
            'completed': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'due': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'})
        },
        u'management.nodechange': {
            'Meta': {'object_name': 'NodeChange', 'db_table': "u'node_change'", 'managed': 'False'},
            'base_path': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'base_rev': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'change_type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node_type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'repos': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rev': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.permission': {
            'Meta': {'object_name': 'Permission', 'db_table': "u'permission'", 'managed': 'False'},
            'action': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'username': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.report': {
            'Meta': {'object_name': 'Report', 'db_table': "u'report'", 'managed': 'False'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.repository': {
            'Meta': {'object_name': 'Repository', 'db_table': "u'repository'", 'managed': 'False'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.revision': {
            'Meta': {'object_name': 'Revision', 'db_table': "u'revision'", 'managed': 'False'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'repos': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rev': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'management.scopebacklog': {
            'Meta': {'object_name': 'ScopeBacklog'},
            'feature_rank': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['management.ScopeBacklogFeatureRank']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'management.scopebacklogfeaturerank': {
            'Meta': {'object_name': 'ScopeBacklogFeatureRank'},
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Feature']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ranking': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'scope_backlog': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['management.ScopeBacklog']"})
        },
        u'management.session': {
            'Meta': {'object_name': 'Session', 'db_table': "u'session'", 'managed': 'False'},
            'authenticated': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_visit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sid': ('django.db.models.fields.TextField', [], {'primary_key': 'True'})
        },
        u'management.sessionattribute': {
            'Meta': {'object_name': 'SessionAttribute', 'db_table': "u'session_attribute'", 'managed': 'False'},
            'authenticated': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sid': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.shouldbeimproved': {
            'Meta': {'object_name': 'ShouldBeImproved'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['management.Session']", 'symmetrical': 'False'}),
            'retrospective': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['management.SprintRetrospective']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'management.sprintplanning': {
            'Meta': {'object_name': 'SprintPlanning'},
            'deadline': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['management.Session']", 'symmetrical': 'False'}),
            'objective': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'tickets': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['management.Ticket']", 'symmetrical': 'False'})
        },
        u'management.sprintplanningtickts': {
            'Meta': {'object_name': 'SprintPlanningTickts'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sprintplanning': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['management.SprintPlanning']"}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['management.Ticket']"})
        },
        u'management.sprintretrospective': {
            'Meta': {'object_name': 'SprintRetrospective'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'management.strongpoint': {
            'Meta': {'object_name': 'StrongPoint'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'retrospective': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['management.SprintRetrospective']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'management.system': {
            'Meta': {'object_name': 'System', 'db_table': "u'system'", 'managed': 'False'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.ticket': {
            'Meta': {'object_name': 'Ticket', 'db_table': "u'ticket'", 'managed': 'False'},
            'cc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'changetime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'component': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'milestone': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reporter': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'resolution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'severity': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.ticketchange': {
            'Meta': {'object_name': 'TicketChange', 'db_table': "u'ticket_change'", 'managed': 'False'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'field': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newvalue': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'oldvalue': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ticket': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'management.ticketcustom': {
            'Meta': {'object_name': 'TicketCustom', 'db_table': "u'ticket_custom'", 'managed': 'False'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ticket': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'management.version': {
            'Meta': {'object_name': 'Version', 'db_table': "u'version'", 'managed': 'False'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'management.wiki': {
            'Meta': {'object_name': 'Wiki', 'db_table': "u'wiki'", 'managed': 'False'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipnr': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'readonly': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['management']