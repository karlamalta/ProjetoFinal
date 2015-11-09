from django.http import HttpResponse
from assets.models import Feature
from django.shortcuts import render_to_response
from django.template import RequestContext

def similar_sibling(feature):
    similar = feature.similar.all()
    if len(similar) > 0:
        siblings = list(feature.get_siblings(include_self=False))
        for i in similar:
            if i in siblings:
                return True
        return False
    else:
        return False   


def fedre(request):
    #Start FeDRE
    if request.method == "POST":
        i = int(request.POST.get('index'))
        features = Feature.objects.all()
        roots = Feature.objects.root_nodes()
        roots_list = list(roots)
        if i < len(roots_list):         
            index = i+1
            node = roots_list[i]
            branch = node.get_descendants(include_self=True)
            must_have_use_case = []
            may_have_use_case = []
            should_not_have_use_case = []
            for f in list(branch):
                #Root and intermediate features
                if (f.is_leaf_node() == False) or (f.is_root_node() == True):
                    if similar_sibling(f) == False:
                        must_have_use_case.append(f)
                    else:
                        should_not_have_use_case.append(f)
                #Leaf features
                else:
                    if f.variability == 'mandatory':
                        if similar_sibling(f) == False:
                            may_have_use_case.append(f)
                        else: 
                            should_not_have_use_case.append(f)
                    else:
                        should_not_have_use_case.append(f)

            context = {
                'features': branch,
                'index': index,
                'must_have_use_case': must_have_use_case,
                'may_have_use_case': may_have_use_case,
                'should_not_have_use_case': should_not_have_use_case,
                      }
            return render_to_response('admin/fedre.html', context, context_instance=RequestContext(request))
        #All braches done
        else:
            context = {}
            return render_to_response('admin/finish_fedre.html', context, context_instance=RequestContext(request))
    #First page
    else:
        context = {}
        return render_to_response('admin/start_fedre.html', context, context_instance=RequestContext(request))
   
