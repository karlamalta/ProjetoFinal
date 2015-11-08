from django.http import HttpResponse
from assets.models import Feature
from django.shortcuts import render_to_response
from django.template import RequestContext

def fedre(request):
    
    if request.method == "POST":
        i = int(request.POST.get('index'))
        features = Feature.objects.all()
        roots = Feature.objects.root_nodes()
        roots_list = list(roots)
        if i < len(roots_list):            
            node = roots_list[i]
            branch = node.get_descendants(include_self=True)
            index = i+1
            context = {
            'features': branch,
            'index': index,
                  }
            return render_to_response('admin/fedre.html', context, context_instance=RequestContext(request))
        else:
            context = {}
            return render_to_response('admin/finish_fedre.html', context, context_instance=RequestContext(request))
    else:
        context = {}
        return render_to_response('admin/start_fedre.html', context, context_instance=RequestContext(request))
   
