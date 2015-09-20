# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Product'
        db.create_table(u'assets_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'assets', ['Product'])

        # Adding M2M table for field features on 'Product'
        db.create_table(u'assets_product_features', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm[u'assets.product'], null=False)),
            ('feature', models.ForeignKey(orm[u'assets.feature'], null=False))
        ))
        db.create_unique(u'assets_product_features', ['product_id', 'feature_id'])

        # Adding model 'Feature'
        db.create_table(u'assets_feature', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('configuration', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('variability', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('binding_time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['configuration.BindingTime'])),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['assets.Feature'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'assets', ['Feature'])

        # Adding M2M table for field requires on 'Feature'
        db.create_table(u'assets_feature_requires', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_feature', models.ForeignKey(orm[u'assets.feature'], null=False)),
            ('to_feature', models.ForeignKey(orm[u'assets.feature'], null=False))
        ))
        db.create_unique(u'assets_feature_requires', ['from_feature_id', 'to_feature_id'])

        # Adding M2M table for field excludes on 'Feature'
        db.create_table(u'assets_feature_excludes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_feature', models.ForeignKey(orm[u'assets.feature'], null=False)),
            ('to_feature', models.ForeignKey(orm[u'assets.feature'], null=False))
        ))
        db.create_unique(u'assets_feature_excludes', ['from_feature_id', 'to_feature_id'])

        # Adding M2M table for field glossary on 'Feature'
        db.create_table(u'assets_feature_glossary', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feature', models.ForeignKey(orm[u'assets.feature'], null=False)),
            ('glossary', models.ForeignKey(orm[u'assets.glossary'], null=False))
        ))
        db.create_unique(u'assets_feature_glossary', ['feature_id', 'glossary_id'])

        # Adding model 'Glossary'
        db.create_table(u'assets_glossary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('definition', self.gf('django.db.models.fields.TextField')(max_length=200)),
        ))
        db.send_create_signal(u'assets', ['Glossary'])

        # Adding model 'Scenario'
        db.create_table(u'assets_scenario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'assets', ['Scenario'])

        # Adding M2M table for field owners on 'Scenario'
        db.create_table(u'assets_scenario_owners', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scenario', models.ForeignKey(orm[u'assets.scenario'], null=False)),
            ('session', models.ForeignKey(orm[u'management.session'], null=False))
        ))
        db.create_unique(u'assets_scenario_owners', ['scenario_id', 'session_id'])

        # Adding M2M table for field features on 'Scenario'
        db.create_table(u'assets_scenario_features', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scenario', models.ForeignKey(orm[u'assets.scenario'], null=False)),
            ('feature', models.ForeignKey(orm[u'assets.feature'], null=False))
        ))
        db.create_unique(u'assets_scenario_features', ['scenario_id', 'feature_id'])

        # Adding M2M table for field dependencies on 'Scenario'
        db.create_table(u'assets_scenario_dependencies', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_scenario', models.ForeignKey(orm[u'assets.scenario'], null=False)),
            ('to_scenario', models.ForeignKey(orm[u'assets.scenario'], null=False))
        ))
        db.create_unique(u'assets_scenario_dependencies', ['from_scenario_id', 'to_scenario_id'])

        # Adding model 'FunctionalSpecification'
        db.create_table(u'assets_functionalspecification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('rationale', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('precondition', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.Feature'])),
        ))
        db.send_create_signal(u'assets', ['FunctionalSpecification'])

        # Adding M2M table for field owner on 'FunctionalSpecification'
        db.create_table(u'assets_functionalspecification_owner', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('functionalspecification', models.ForeignKey(orm[u'assets.functionalspecification'], null=False)),
            ('session', models.ForeignKey(orm[u'management.session'], null=False))
        ))
        db.create_unique(u'assets_functionalspecification_owner', ['functionalspecification_id', 'session_id'])

        # Adding M2M table for field scenarios on 'FunctionalSpecification'
        db.create_table(u'assets_functionalspecification_scenarios', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('functionalspecification', models.ForeignKey(orm[u'assets.functionalspecification'], null=False)),
            ('scenario', models.ForeignKey(orm[u'assets.scenario'], null=False))
        ))
        db.create_unique(u'assets_functionalspecification_scenarios', ['functionalspecification_id', 'scenario_id'])

        # Adding M2M table for field mainSteps on 'FunctionalSpecification'
        db.create_table(u'assets_functionalspecification_mainSteps', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('functionalspecification', models.ForeignKey(orm[u'assets.functionalspecification'], null=False)),
            ('mainsteps', models.ForeignKey(orm[u'assets.mainsteps'], null=False))
        ))
        db.create_unique(u'assets_functionalspecification_mainSteps', ['functionalspecification_id', 'mainsteps_id'])

        # Adding M2M table for field alternativeSteps on 'FunctionalSpecification'
        db.create_table(u'assets_functionalspecification_alternativeSteps', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('functionalspecification', models.ForeignKey(orm[u'assets.functionalspecification'], null=False)),
            ('alternativesteps', models.ForeignKey(orm[u'assets.alternativesteps'], null=False))
        ))
        db.create_unique(u'assets_functionalspecification_alternativeSteps', ['functionalspecification_id', 'alternativesteps_id'])

        # Adding M2M table for field exceptionSteps on 'FunctionalSpecification'
        db.create_table(u'assets_functionalspecification_exceptionSteps', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('functionalspecification', models.ForeignKey(orm[u'assets.functionalspecification'], null=False)),
            ('exceptionsteps', models.ForeignKey(orm[u'assets.exceptionsteps'], null=False))
        ))
        db.create_unique(u'assets_functionalspecification_exceptionSteps', ['functionalspecification_id', 'exceptionsteps_id'])

        # Adding model 'MainSteps'
        db.create_table(u'assets_mainsteps', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('functional_specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.FunctionalSpecification'])),
            ('user_action', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('system_response', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'assets', ['MainSteps'])

        # Adding model 'AlternativeSteps'
        db.create_table(u'assets_alternativesteps', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('functional_specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.FunctionalSpecification'])),
            ('user_action', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('system_response', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'assets', ['AlternativeSteps'])

        # Adding model 'ExceptionSteps'
        db.create_table(u'assets_exceptionsteps', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('functional_specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.FunctionalSpecification'])),
            ('user_action', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('system_response', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'assets', ['ExceptionSteps'])

        # Adding model 'TestExecution'
        db.create_table(u'assets_testexecution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('functional_specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assets.FunctionalSpecification'])),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'assets', ['TestExecution'])


    def backwards(self, orm):
        # Deleting model 'Product'
        db.delete_table(u'assets_product')

        # Removing M2M table for field features on 'Product'
        db.delete_table('assets_product_features')

        # Deleting model 'Feature'
        db.delete_table(u'assets_feature')

        # Removing M2M table for field requires on 'Feature'
        db.delete_table('assets_feature_requires')

        # Removing M2M table for field excludes on 'Feature'
        db.delete_table('assets_feature_excludes')

        # Removing M2M table for field glossary on 'Feature'
        db.delete_table('assets_feature_glossary')

        # Deleting model 'Glossary'
        db.delete_table(u'assets_glossary')

        # Deleting model 'Scenario'
        db.delete_table(u'assets_scenario')

        # Removing M2M table for field owners on 'Scenario'
        db.delete_table('assets_scenario_owners')

        # Removing M2M table for field features on 'Scenario'
        db.delete_table('assets_scenario_features')

        # Removing M2M table for field dependencies on 'Scenario'
        db.delete_table('assets_scenario_dependencies')

        # Deleting model 'FunctionalSpecification'
        db.delete_table(u'assets_functionalspecification')

        # Removing M2M table for field owner on 'FunctionalSpecification'
        db.delete_table('assets_functionalspecification_owner')

        # Removing M2M table for field scenarios on 'FunctionalSpecification'
        db.delete_table('assets_functionalspecification_scenarios')

        # Removing M2M table for field mainSteps on 'FunctionalSpecification'
        db.delete_table('assets_functionalspecification_mainSteps')

        # Removing M2M table for field alternativeSteps on 'FunctionalSpecification'
        db.delete_table('assets_functionalspecification_alternativeSteps')

        # Removing M2M table for field exceptionSteps on 'FunctionalSpecification'
        db.delete_table('assets_functionalspecification_exceptionSteps')

        # Deleting model 'MainSteps'
        db.delete_table(u'assets_mainsteps')

        # Deleting model 'AlternativeSteps'
        db.delete_table(u'assets_alternativesteps')

        # Deleting model 'ExceptionSteps'
        db.delete_table(u'assets_exceptionsteps')

        # Deleting model 'TestExecution'
        db.delete_table(u'assets_testexecution')


    models = {
        u'assets.alternativesteps': {
            'Meta': {'object_name': 'AlternativeSteps'},
            'functional_specification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.FunctionalSpecification']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'system_response': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user_action': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'assets.exceptionsteps': {
            'Meta': {'object_name': 'ExceptionSteps'},
            'functional_specification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.FunctionalSpecification']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'system_response': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user_action': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
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
        u'assets.functionalspecification': {
            'Meta': {'object_name': 'FunctionalSpecification'},
            'alternativeSteps': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'alternativesteps_funcspec'", 'blank': 'True', 'to': u"orm['assets.AlternativeSteps']"}),
            'exceptionSteps': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'exceptionsteps_funcspec'", 'blank': 'True', 'to': u"orm['assets.ExceptionSteps']"}),
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.Feature']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mainSteps': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'mainsteps_funcspec'", 'blank': 'True', 'to': u"orm['assets.MainSteps']"}),
            'owner': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['management.Session']", 'symmetrical': 'False'}),
            'precondition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rationale': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'scenarios': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['assets.Scenario']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'assets.glossary': {
            'Meta': {'object_name': 'Glossary'},
            'definition': ('django.db.models.fields.TextField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'assets.mainsteps': {
            'Meta': {'object_name': 'MainSteps'},
            'functional_specification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.FunctionalSpecification']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'system_response': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user_action': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'assets.product': {
            'Meta': {'object_name': 'Product'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'features': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'features_productmaps'", 'blank': 'True', 'to': u"orm['assets.Feature']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'assets.scenario': {
            'Meta': {'object_name': 'Scenario'},
            'dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'dependencies_scenario'", 'blank': 'True', 'to': u"orm['assets.Scenario']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'features': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['assets.Feature']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['management.Session']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'assets.testexecution': {
            'Meta': {'object_name': 'TestExecution'},
            'functional_specification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assets.FunctionalSpecification']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'configuration.bindingtime': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BindingTime'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'management.session': {
            'Meta': {'object_name': 'Session', 'db_table': "u'session'", 'managed': 'False'},
            'authenticated': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_visit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sid': ('django.db.models.fields.TextField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['assets']