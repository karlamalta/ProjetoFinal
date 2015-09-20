# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BindingTime'
        db.create_table(u'configuration_bindingtime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'configuration', ['BindingTime'])

        # Adding model 'FeatureType'
        db.create_table(u'configuration_featuretype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'configuration', ['FeatureType'])


    def backwards(self, orm):
        # Deleting model 'BindingTime'
        db.delete_table(u'configuration_bindingtime')

        # Deleting model 'FeatureType'
        db.delete_table(u'configuration_featuretype')


    models = {
        u'configuration.bindingtime': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BindingTime'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'configuration.featuretype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'FeatureType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['configuration']