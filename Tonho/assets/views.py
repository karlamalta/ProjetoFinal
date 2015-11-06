from django.http import HttpResponse
from assets.models import Feature
from django.shortcuts import render_to_response
from django.template import RequestContext

def fedre(request):
    
    features = Feature.objects.all()
    roots = Feature.objects.root_nodes()
    roots_list = list(roots)
    node = roots_list[0]
    #node = roots[2:3].get()
    branch = node.get_descendants(include_self=True)
    
    
    context = {
        'features': branch,
              }
    return render_to_response('admin/fedre.html', context, context_instance=RequestContext(request))
   
