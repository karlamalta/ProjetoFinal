from django.db import models
from management.tracdb import Session
from mptt.models import MPTTModel, TreeForeignKey
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from assets.util import render_to_latex


class Meta:
       app_label = 'Tasks'
       
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    features = models.ManyToManyField('Feature', blank=True, symmetrical=False)
    def __unicode__(self):
        return self.name
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

VARIABILITY_CHOICES = (('mandatory', 'Mandatory'),
                    ('optional', 'Optional'),
                    ('alternative', 'Alternative'))
TYPE_CHOICES = (('abstract', 'Abstract'),
                    ('concrete', 'Concrete'))
class Feature(MPTTModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    configuration = models.CharField(max_length=200)  
    
    variability = models.CharField(max_length=20, choices=VARIABILITY_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    binding_time = models.ForeignKey('configuration.BindingTime')

    parent  = TreeForeignKey('self', blank=True, null=True, related_name='children')
    requires = models.ManyToManyField("self", blank=True, symmetrical=False, 
                                      related_name='requires_features')
    excludes = models.ManyToManyField("self", blank=True, symmetrical=False, 
                                      related_name='excludes_features')
                                      
    glossary = models.ManyToManyField('Glossary', blank=True)
    def __unicode__(self):
        return "#" + str(self.id) + " "  + self.name
    class MPTTMeta:
        order_insertion_by = ['name']    
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

    @staticmethod
    def getReport(product=None):
        if(product):
            mycontext = {'features': product.features.all,
                         'product_name': product.name,
                   'autoescape': False}
        else:
            mycontext = {'features': Feature.objects.all,
                         'product_name': "All products",
                    'autoescape': False}
        return render_to_latex("admin/fur/feature/report_features.tex",mycontext)

        
class Glossary(models.Model):
    term = models.CharField(max_length=200)
    definition = models.TextField(max_length=200)        
 
    class Meta:
        verbose_name = 'Glossary Item'
        verbose_name_plural = 'Glossary' 
    def __unicode__(self):
        return self.term    
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    @staticmethod
    def getReport(product=None):
        if(product):
            mycontext = {'glossary': Glossary.objects.filter(feature__in=product.features.all).distinct(),
                         'product_name': product.name,
                   'autoescape': False}
        else:
            mycontext = {'glossary': Glossary.objects.all,
                         'product_name': "All products",
                    'autoescape': False}

        return render_to_latex("admin/fur/glossary/report_glossary.tex",mycontext)
    
class UseCase(models.Model):

    title = models.CharField(max_length=200, verbose_name="Use Case Name")
    description = models.TextField(blank=True)
    precondition = models.TextField(max_length=200, blank=True, verbose_name="Pre-condition")
    postcondition = models.TextField(max_length=200, blank=True, verbose_name="Post-condition")
    actors = models.TextField(max_length=200, blank=True, verbose_name="Actors")
    owner = models.ManyToManyField(Session, limit_choices_to={'authenticated': '1'})
    feature = models.ManyToManyField(Feature, verbose_name="Associated Features")
    includesTo = models.ManyToManyField("self", blank=True, verbose_name="Includes To")
    extendsFrom= models.ManyToManyField("self", blank=True, verbose_name="Extends From")
    mainSteps = models.ManyToManyField('MainSteps', blank=True, symmetrical=False, related_name='mainsteps_funcspec')
    alternativeSteps = models.ManyToManyField('AlternativeSteps', blank=True, symmetrical=False, related_name='alternativesteps_funcspec')
    alternativeScenarios = models.ManyToManyField('AlternativeScenarios', blank=True, symmetrical=False, related_name='alternativescenarios_funcspec')

    def __unicode__(self):
        return self.title
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

    @staticmethod
    def getReport(product=None):
        if(product):
            mycontext = {'usecases': UseCase.objects.filter(feature__in=product.features.all),
                         'product_name': product.name,
                   'autoescape': False}
        else:
            mycontext = {'usecases': UseCase.objects.all,
                         'product_name': "All products",
                    'autoescape': False}

        return render_to_latex("admin/fur/usecase/report_usecase.tex",mycontext)

class TestCase(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=False)
    owner = models.ManyToManyField(Session)
    use_case = models.ForeignKey(UseCase)
    expected_result = models.TextField(blank=False)
    steps = models.ManyToManyField('TestSteps', blank=True, symmetrical=False)


    def __unicode__(self):
        return self.title
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    @staticmethod
    def getReport(product=None):
        if(product):
            mycontext = {'testCases': TestCase.objects.filter(use_case__in=UseCase.objects.filter(feature__in=product.features.all)).distinct(),
                         'product_name': product.name,
                   'autoescape': False}
        else:
            mycontext = {'testCases': TestCase.objects.all,
                         'product_name': "All products",
                    'autoescape': False}

        return render_to_latex("admin/fur/testcase/report_testcase.tex",mycontext)

class TestSteps(models.Model):
    test_case = models.ForeignKey(TestCase)
    description = models.TextField(blank=False)
    def __unicode__(self):
        return self.description
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class MainSteps(models.Model):    
    use_case = models.ForeignKey(UseCase)
    step_number = models.CharField(max_length=2,verbose_name="Step") 
    user_action = models.TextField(verbose_name="Actor Action")
    system_response = models.TextField(verbose_name="Blackbox System Response")
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    def __unicode__(self):
        return "Main Step"

class AlternativeScenarios(models.Model):
    use_case = models.ForeignKey(UseCase)
    scenario_name = models.TextField(verbose_name="Alternative Scenario Name")
    condition = models.TextField(verbose_name="Condition")
    associated_features = models.ManyToManyField(Feature, verbose_name="Associated Features")
    #alternative_steps = models.ManyToManyField('AlternativeSteps', blank=True, symmetrical=False, related_name='alternativesteps_funcspec')
    def __unicode__(self):
        return self.title
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class AlternativeSteps(models.Model):    
    use_case = models.ForeignKey(UseCase)
    #step_number = models.CharField(max_length=2, verbose_name="Step")
    user_action = models.TextField()
    system_response = models.TextField()
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    def __unicode__(self):
        return "Alternative Step"

STATUS_CHOICES = (('pass', 'Passed'),
                    ('failed', 'Failed'))
class TestExecution(models.Model):    
    test_case = models.ForeignKey(TestCase)
    result = models.CharField(max_length=20, choices=STATUS_CHOICES)
    def __unicode__(self):
        return "Test execution " + str(self.id)
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class UserStory(models.Model):
    name = models.CharField(max_length=200)
    features = models.ManyToManyField(Feature)
    as_a = models.CharField(max_length=200)
    i_want = models.TextField()
    so_that = models.TextField()
    constraints = models.ManyToManyField('Constraint', blank=True, symmetrical=False,
                                      related_name='constraints_userstory')
    def __unicode__(self):
        return self.name

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    class Meta:
        verbose_name = 'User story'
        verbose_name_plural = 'User stories'
    @staticmethod
    def getReport(product=None):
        if(product):
            mycontext = {'userStories': UserStory.objects.filter(features__in=product.features.all).distinct(),
                         'product_name': product.name,
                   'autoescape': False}
        else:
            mycontext = {'userStories': UserStory.objects.all,
                         'product_name': "All products",
                    'autoescape': False}

        return render_to_latex("admin/fur/userstory/report_userstory.tex",mycontext)


class Constraint(models.Model):
    user_story = models.ForeignKey(UserStory)
    restriction_n = models.TextField()
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class AcceptanceTest(models.Model):
    name = models.CharField(max_length=200)
    user_story = models.ForeignKey(UserStory)
    given = models.TextField()
    when = models.TextField()
    then = models.TextField()
    def __unicode__(self):
        return self.name

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class AcceptanceTestExecution(models.Model):
    acceptance_test = models.ForeignKey(AcceptanceTest)
    date = date =  models.DateField()
    result = models.CharField(max_length=20, choices=STATUS_CHOICES)
    observation = models.TextField()

    def __unicode__(self):
        return str(self.date)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class Note(models.Model):    
    title = models.CharField(max_length=200)
    date = date =  models.DateField()
    note = models.TextField()
    release = models.ForeignKey('management.Version')
    result = models.CharField(max_length=20, choices=STATUS_CHOICES)
    def __unicode__(self):
        return self.title
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    
