from django.contrib import admin
from projects.models import *
from django.contrib.auth.models import * 
class ProductAdmin(admin.ModelAdmin):
    fields = ['name', 'description','configuration']

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
    fields = ['name', 'description', 'type', 'variability'  , 'bindingTime' , 'father' , 'glossary']
    inlines = [ FeatureRequireAdminInline, FeatureExcludeAdminInline, ]
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class BindingTimeAdmin(admin.ModelAdmin):
    fields = ['name','description']
    
class FeatureVariabilityTypeAdmin(admin.ModelAdmin):
    fields = ['name','description']    

class FeatureTypeAdmin(admin.ModelAdmin):
    fields = ['name','description']  
    
    
class ProductMapFeaturesAdminInline(admin.TabularInline):
    model = ProductMap.features.through
    verbose_name_plural = 'Features'
    verbose_name = 'Feature'
    extra = 0
    
class ProductMapAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [ ProductMapFeaturesAdminInline, ]
	
class GlossaryAdmin(admin.ModelAdmin):
    fields = ['term','definition']

class FeatureRankScopeBacklogAdminInline(admin.TabularInline):
    model = ScopeBacklogFeatureRank
    verbose_name_plural = 'Features rank'
    verbose_name = 'Features rank'
    #fk_name = 'scopeBacklog'
    extra = 0
    
class ScopeBacklogAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [ FeatureRankScopeBacklogAdminInline ]

class ScenarioFeaturesAdminInline(admin.TabularInline):
    model = Scenario.features.through
    verbose_name_plural = 'Features'
    verbose_name = 'Feature'
    extra = 0
    
class ScenarioDependenciesAdminInline(admin.TabularInline):
    model = Scenario.dependencies.through
    verbose_name_plural = 'Dependencies'
    verbose_name = 'Dependency'
    fk_name = 'from_scenario'
    extra = 0
    
class ScenarioAdmin(admin.ModelAdmin):
    fields = ['description','owners']
    inlines = [ ScenarioFeaturesAdminInline,ScenarioDependenciesAdminInline ]

class FunctionalSpecificationMainStepsAdminInline(admin.TabularInline):
    model = MainSteps
    verbose_name_plural = 'Main Step'
    verbose_name = 'Main Steps'
    #fk_name = 'scopeBacklog'
    extra = 0

class FunctionalSpecificationAlternativeStepsAdminInline(admin.TabularInline):
    model = AlternativeSteps
    verbose_name_plural = 'Secondary Step'
    verbose_name = 'Secondary Steps'
    #fk_name = 'scopeBacklog'
    extra = 0    

class FunctionalSpecificationExceptionStepsAdminInline(admin.TabularInline):
    model = ExceptionSteps
    verbose_name_plural = 'Exception Step'
    verbose_name = 'Exception rank'
    #fk_name = 'scopeBacklog'
    extra = 0    
    
class FunctionalSpecificationAdmin(admin.ModelAdmin):
    fields = ['title','rationale','owner','scenarios','feature'
    ,'precondition']
    inlines = [ FunctionalSpecificationMainStepsAdminInline,FunctionalSpecificationAlternativeStepsAdminInline,FunctionalSpecificationExceptionStepsAdminInline  ]
  
class TestExecutionAdmin(admin.ModelAdmin):
    fields = ['functionalSpecification','result']
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(Product, ProductAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(BindingTime, BindingTimeAdmin)
admin.site.register(FeatureVariabilityType, FeatureVariabilityTypeAdmin)
admin.site.register(FeatureType, FeatureTypeAdmin)
admin.site.register(ProductMap, ProductMapAdmin)
admin.site.register(Glossary, GlossaryAdmin)
admin.site.register(ScopeBacklog, ScopeBacklogAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(FunctionalSpecification, FunctionalSpecificationAdmin)
admin.site.register(TestExecution, TestExecutionAdmin)