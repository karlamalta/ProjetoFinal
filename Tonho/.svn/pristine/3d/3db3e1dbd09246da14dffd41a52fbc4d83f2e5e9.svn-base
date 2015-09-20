from trac.core import *
from trac.web.chrome import INavigationContributor, ITemplateProvider
from trac.util import Markup

class NavAdd(Component):
    """ Allows to add items to main and meta navigation bar"""
    implements(INavigationContributor)

    nav_contributors = ExtensionPoint(INavigationContributor)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return ''
                
    def get_navigation_items(self, req):
	add = self.env.config.get('navadd', 'add_items', ''). \
		replace(',', ' ').split()
	
	items = []
	for a in add:
	    title = self.env.config.get('navadd', '%s.title' % a)
	    url = self.env.config.get('navadd', '%s.url' % a)
	    perm = self.env.config.get('navadd', '%s.perm' % a)
	    target = self.env.config.get('navadd', '%s.target' % a)

	    if perm and not req.perm.has_permission(perm):
		continue

	    if target not in ('mainnav', 'metanav'):
		target = 'mainnav'

	    items.append((target, a, Markup('<a href="%s">%s</a>' % (url, title))))
	
	return items
