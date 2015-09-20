from setuptools import setup

setup(name='NavAdd',
      version='0.1',
      packages=['navadd'],
      entry_points = {'trac.plugins': ['navadd = navadd']},
      package_data={'navadd' : ['templates/*.cs', 'htdocs/js/*.js', 'htdocs/css/*.css']},
      author = 'Michael Renzmann',
      author_email = 'mrenzmann@otaku42.de',
      description = 'A plugin for adding navigation items into one of the navigation bars.',
      license = 'BSD',
      keywords = 'trac navigation main meta',
      url = 'http://trac-hacks.org/wiki/NavAddPlugin')
