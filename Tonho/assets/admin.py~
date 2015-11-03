from django.contrib import admin
from assets.models import *
from django.contrib.auth.models import * 
from django import forms
from django.forms import *
from mptttreewidget.widget import MpttTreeWidget
from django.forms import TextInput, Textarea
from django.db import models

from django.shortcuts import render_to_response
from django.contrib.admin import helpers
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.template import RequestContext
from assets.util import render_to_latex
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile

#from nested_inlines.admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

import os
import zipfile
import StringIO
import codecs
#import nested_admin


class FeatureExcludeAdminInline(admin.TabularInline):
    model = Feature.excludes.through
    verbose_name_plural = 'Excluded features'
    verbose_name = 'Excluded feature'
    #I got the fk_name using the django shell, by inspecting the objet Feature
    fk_name = 'from_feature'
    extra = 0
    #form = ExcludedFeaturesForm
    
class FeatureRequireAdminInline(admin.TabularInline):
    model = Feature.requires.through
    verbose_name_plural = 'Required features'
    verbose_name = 'Required feature'
    #I gor the fk_name using the django shell, by inspecting the objet Feature
    fk_name = 'from_feature'
    extra = 0
    #form = RequiredFeaturesForm    
    
class FeatureAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'type', 'variability'  , 'binding_time' , 'parent' , 'glossary']
    inlines = [ FeatureRequireAdminInline, FeatureExcludeAdminInline, ]
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    filter_horizontal = ("glossary",)
    list_filter = ('type', 'variability')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_report'] = True
        return super(FeatureAdmin, self).changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            if request.REQUEST.has_key("_report"):
                body = Feature.getReport()
                resp = HttpResponse(body, mimetype='application/pdf')
                resp['Content-Disposition'] = 'attachment; filename=features_report.pdf'
                return resp
            else:
                feature = Feature.objects.get(id=object_id)
                context = {
                    'feature': feature,
                    'title': _('Feature: %s') % force_unicode(feature.name),
                    'opts': opts,
                    'object_id': object_id,
                    'is_popup': request.REQUEST.has_key('_popup'),
                    'app_label': opts.app_label,
                    }
                return render_to_response('admin/fur/feature/view.html',
                                          context,
                                          context_instance=RequestContext(request))
        return super(FeatureAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)

class ProductMapForm(ModelForm):
    features = ModelMultipleChoiceField(required=False, queryset=Feature.objects.all(), widget=MpttTreeWidget)

    class Meta:
        model = Feature
        
class ProductAdmin(admin.ModelAdmin):
    #fields = ['name', 'description','configuration'] 
    form = ProductMapForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField',})},
    }
    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            if request.REQUEST.has_key("_zipreport"):
                product = Product.objects.get(id=object_id)
                #use case
                usecase = UseCase.getReport(product)
                usecaseTemp = NamedTemporaryFile()
                usecaseTemp.close()
                usecaseTemp = codecs.open(usecaseTemp.name,'wb')
                usecaseTemp.write(usecase)
                usecaseTemp.close()

                #Feature
                features = Feature.getReport(Product.objects.get(id=object_id))
                featuresTemp = NamedTemporaryFile()
                featuresTemp.close()
                featuresTemp = codecs.open(featuresTemp.name,'wb')
                featuresTemp.write(features)
                featuresTemp.close()

                #Glossary
                glossary = Glossary.getReport(Product.objects.get(id=object_id))
                glossaryTemp = NamedTemporaryFile()
                glossaryTemp.close()
                glossaryTemp = codecs.open(glossaryTemp.name,'wb')
                glossaryTemp.write(glossary)
                glossaryTemp.close()

                #Test Case
                testCase = TestCase.getReport(Product.objects.get(id=object_id))
                testCaseTemp = NamedTemporaryFile()
                testCaseTemp.close()
                testCaseTemp = codecs.open(testCaseTemp.name,'wb')
                testCaseTemp.write(testCase)
                testCaseTemp.close()


                #User story
                userStory = UserStory.getReport(Product.objects.get(id=object_id))
                userStoryTemp = NamedTemporaryFile()
                userStoryTemp.close()
                userStoryTemp = codecs.open(userStoryTemp.name,'wb')
                userStoryTemp.write(userStory)
                userStoryTemp.close()


                # Folder name in ZIP archive which contains the above files
                # E.g [thearchive.zip]/somefiles/file2.txt
                # FIXME: Set this to something better
                zip_subdir = product.name.replace(" ", "_")+"_artifacs"
                zip_filename = "%s.zip" % zip_subdir

                # Open StringIO to grab in-memory ZIP contents
                s = StringIO.StringIO()

                # The zip compressor
                zf = zipfile.ZipFile(s, "w")

                # Calculate path for file in zip
                usecase_zip_path = os.path.join(zip_subdir, product.name+ "_usecase_report.pdf")
                feature_zip_path = os.path.join(zip_subdir, product.name+ "_features_report.pdf")
                glossary_zip_path = os.path.join(zip_subdir, product.name+ "_glossary_report.pdf")
                testCase_zip_path = os.path.join(zip_subdir, product.name+ "_testCase_report.pdf")
                userStory_zip_path = os.path.join(zip_subdir, product.name+ "_userStory_report.pdf")

                # Add file, at correct path
                zf.write(usecaseTemp.name, usecase_zip_path)
                zf.write(featuresTemp.name, feature_zip_path)
                zf.write(glossaryTemp.name, glossary_zip_path)
                zf.write(testCaseTemp.name, testCase_zip_path)
                zf.write(userStoryTemp.name, userStory_zip_path)

                # Must close zip for all contents to be written
                zf.close()

                # Grab ZIP file from in-memory, make response with correct MIME-type
                resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
                # ..and correct content-disposition
                resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
                return resp
            else:
                product = Product.objects.get(id=object_id)
                context = {
                    'product': product,
                    'title': _('Product: %s') % force_unicode(product.name),
                    'opts': opts,
                    'object_id': object_id,
                    'is_popup': request.REQUEST.has_key('_popup'),
                    'app_label': opts.app_label,
                    }
                return render_to_response('admin/fur/product/view.html',
                                          context,
                                          context_instance=RequestContext(request))
        return super(ProductAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)

	
class GlossaryAdmin(admin.ModelAdmin):
    fields = ['term','definition']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_report'] = True
        return super(GlossaryAdmin, self).changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            if request.REQUEST.has_key("_report"):
                body = Glossary.getReport()
                resp = HttpResponse(body, mimetype='application/pdf')
                resp['Content-Disposition'] = 'attachment; filename=glossary_report.pdf'
                return resp
            else:
                glossary = Glossary.objects.get(id=object_id)
                context = {
                    'glossary': glossary,
                    'title': _('Glossary: %s') % force_unicode(glossary.term),
                    'opts': opts,
                    'object_id': object_id,
                    'is_popup': request.REQUEST.has_key('_popup'),
                    'app_label': opts.app_label,
                    }
                return render_to_response('admin/fur/glossary/view.html',
                                          context,
                                          context_instance=RequestContext(request))
        return super(GlossaryAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)


class UseCaseMainStepsAdminInline(admin.TabularInline):
    model = MainSteps
    verbose_name_plural = 'Main Success Scenario'
    verbose_name = 'Step'
    fk_name = 'use_case'
    extra = 0
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField'})},
        models.CharField: {'widget': TextInput(attrs={'size':2})}
    }

class UseCaseStepsAdminInline(admin.TabularInline):
    model = AlternativeSteps
    verbose_name_plural = 'Alternative Scenario Steps'
    verbose_name = 'Step'
    fk_name = 'use_case'
    extra = 0       
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField'})},
        models.CharField: {'widget': TextInput(attrs={'size':2})}
    }

class UseCaseAlternativeScenariosAdminInline(admin.StackedInline):
    model = AlternativeScenarios
    verbose_name_plural = 'Alternative Scenarios'
    verbose_name = 'Alternative Scenario'
    fk_name = 'use_case'
    extra = 0
    filter_horizontal = ("associated_features", )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField',})},
    }
    #Link to Alternative Scenario edit page
    readonly_fields = ('changeform_link', )

class UseCaseAlternativeScenariosAdmin(admin.ModelAdmin):
    verbose_name_plural = 'Alternative Scenarios'
    verbose_name = 'Alternative Scenario'
    filter_horizontal = ("associated_features", )
    inlines = [UseCaseStepsAdminInline,]

class UseCaseAdmin(admin.ModelAdmin):
    fields = ['title','description','owner','feature','actors','precondition', 'postcondition','includesTo','extendsFrom']
    inlines = [ UseCaseMainStepsAdminInline, UseCaseAlternativeScenariosAdminInline]
    filter_horizontal = ("owner","feature","includesTo","extendsFrom")
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField',})},
    }
    list_filter = ('owner',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_report'] = True
        return super(UseCaseAdmin, self).changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            if request.REQUEST.has_key("_report"):
                body = UseCase.getReport()
                resp = HttpResponse(body, mimetype='application/pdf')
                resp['Content-Disposition'] = 'attachment; filename=usecase_report.pdf'
                return resp
            else:
                use_case = UseCase.objects.get(id=object_id)
                context = {
                    'use_case': use_case,
                    'title': _('Use Case: %s') % force_unicode(use_case.title),
                    'opts': opts,
                    'object_id': object_id,
                    'is_popup': request.REQUEST.has_key('_popup'),
                    'app_label': opts.app_label,
                    }
                return render_to_response('admin/fur/usecase/view.html',
                                          context,
                                          context_instance=RequestContext(request))
        return super(UseCaseAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)

class TestCaseStepsAdminInline(admin.TabularInline):
    model = TestSteps
    verbose_name_plural = 'Steps'
    verbose_name = 'Step'
    #fk_name = 'scopeBacklog'
    extra = 0


class TestCaseAdmin(admin.ModelAdmin):
    fields = ['title','description','owner','use_case'
    ,'expected_result']
    inlines = [ TestCaseStepsAdminInline  ]
    filter_horizontal = ("owner",)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField',})},
    }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_report'] = True
        return super(TestCaseAdmin, self).changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            if request.REQUEST.has_key("_report"):
                body = TestCase.getReport()
                resp = HttpResponse(body, mimetype='application/pdf')
                resp['Content-Disposition'] = 'attachment; filename=testcase_report.pdf'
                return resp
            else:
                testcase = TestCase.objects.get(id=object_id)
                context = {
                'testcase': testcase,
                'title': _('Test Case: %s') % force_unicode(testcase.title),
                'opts': opts,
                'object_id': object_id,
                'is_popup': request.REQUEST.has_key('_popup'),
                'app_label': opts.app_label,
                }
                return render_to_response('admin/fur/testcase/view.html',
                                      context,
                                      context_instance=RequestContext(request))
        return super(TestCaseAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)

class TestCaseConstraintsAdminInline(admin.TabularInline):
    model = Constraint
    verbose_name_plural = 'Constraints'
    verbose_name = 'Constraint'
    #fk_name = 'scopeBacklog'
    extra = 0

class UserStoryAdmin(admin.ModelAdmin):
    fields = ['name','as_a','i_want','features','so_that']
    inlines = [ TestCaseConstraintsAdminInline  ]
    verbose_name_plural = 'User stories'
    verbose_name = 'User story'
    filter_horizontal = ("features",)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField',})},
    }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_report'] = True
        return super(UserStoryAdmin, self).changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            if request.REQUEST.has_key("_report"):
                body = UserStory.getReport()
                resp = HttpResponse(body, mimetype='application/pdf')
                resp['Content-Disposition'] = 'attachment; filename=userstory_report.pdf'
                return resp
            else:
                user_story = UserStory.objects.get(id=object_id)
                context = {
                    'user_story': user_story,
                    'title': _('User Story: %s') % force_unicode(user_story.name),
                    'opts': opts,
                    'object_id': object_id,
                    'is_popup': request.REQUEST.has_key('_popup'),
                    'app_label': opts.app_label,
                    }
                return render_to_response('admin/fur/userstory/view.html',
                                      context,
                                      context_instance=RequestContext(request))
            return super(UserStoryAdmin, self).change_view(request, object_id,
                    form_url, extra_context=None)


class AcceptanceTestAdmin(admin.ModelAdmin):
    fields = ['name','user_story','given','when'
    ,'then']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField',})},
    }
    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            acceptance_test = AcceptanceTest.objects.get(id=object_id)
            context = {
                'acceptance_test': acceptance_test,
                'title': _('Acceptance Test: %s') % force_unicode(acceptance_test.name),
                'opts': opts,
                'object_id': object_id,
                'is_popup': request.REQUEST.has_key('_popup'),
                'app_label': opts.app_label,
                }
            return render_to_response('admin/fur/acceptanceTest/view.html',
                                      context,
                                      context_instance=RequestContext(request))
        return super(AcceptanceTestAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)

class AcceptanceTestExecutionAdmin(admin.ModelAdmin):
    fields = ['acceptance_test','date','result','observation']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40,'class':'vLargeTextField',})},
    }
    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            test_execution = AcceptanceTestExecution.objects.get(id=object_id)
            context = {
                'test_execution': test_execution,
                'title': _('Test execution: %s') % force_unicode(str(test_execution.date)),
                'opts': opts,
                'object_id': object_id,
                'is_popup': request.REQUEST.has_key('_popup'),
                'app_label': opts.app_label,
                }
            return render_to_response('admin/fur/acceptanceTestExecution/view.html',
                                      context,
                                      context_instance=RequestContext(request))
        return super(AcceptanceTestExecutionAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)

class NoteAdmin(admin.ModelAdmin):
    fields = ['title','date','note','release']
    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            note = Note.objects.get(id=object_id)
            context = {
                'note': note,
                'title': _('Note: %s') % force_unicode(note.title),
                'opts': opts,
                'object_id': object_id,
                'is_popup': request.REQUEST.has_key('_popup'),
                'app_label': opts.app_label,
                }
            return render_to_response('admin/fur/note/view.html',
                                      context,
                                      context_instance=RequestContext(request))
        return super(NoteAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)
  
class TestExecutionAdmin(admin.ModelAdmin):
    fields = ['test_case','result']
    def change_view(self, request, object_id, form_url='', extra_context=None):
        opts = self.model._meta
        if not request.REQUEST.has_key("_change"):
            test = TestExecution.objects.get(id=object_id)
            context = {
                'test': test,
                'title': _('Test execution: %s') % force_unicode(test),
                'opts': opts,
                'object_id': object_id,
                'is_popup': request.REQUEST.has_key('_popup'),
                'app_label': opts.app_label,
                }
            return render_to_response('admin/fur/testExecution/view.html',
                                      context,
                                      context_instance=RequestContext(request))
        return super(TestExecutionAdmin, self).change_view(request, object_id,
            form_url, extra_context=None)

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(Product, ProductAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Glossary, GlossaryAdmin)
admin.site.register(UseCase, UseCaseAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(TestExecution, TestExecutionAdmin)
admin.site.register(UserStory, UserStoryAdmin)
admin.site.register(AcceptanceTest, AcceptanceTestAdmin)
admin.site.register(AcceptanceTestExecution, AcceptanceTestExecutionAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(AlternativeScenarios,UseCaseAlternativeScenariosAdmin)

