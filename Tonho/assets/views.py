from django.http import HttpResponse
from assets.models import Feature
from django.shortcuts import render_to_response
from django.template import RequestContext
#from django.forms import *
#from mptttreewidget.widget import MpttTreeWidget

def fedre(request):
    #features = ModelMultipleChoiceField(required=False, queryset=Feature.objects.all(), widget=MpttTreeWidget)
    features = Feature.objects.all()
    #output = ', '.join([f.name for f in features])
    context = {
        'features': features,
              }
    return render_to_response('admin/fedre.html', context, context_instance=RequestContext(request))
    #return HttpResponse(output)
    #return HttpResponse("Hello, world. You're at the fedre index.")
