#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2009 Jeff Hammel <jhammel@openplans.org>
# Copyright (C) 2012 Ryan J Ollos <ryan.j.ollos@gmail.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from setuptools import find_packages, setup

version = '0.4.2'

setup(name='AutocompleteUsers',
      version=version,
      description="complete the known trac users, AJAX style",
      author='Jeff Hammel',
      author_email='jhammel@openplans.org',
      maintainer='Ryan J Ollos',
      maintainer_email='ryan.j.ollos@gmail.com',
      url='http://trac-hacks.org/wiki/AutocompleteUsersPlugin',
      keywords='trac plugin',
      license='BSD 3-Clause',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests*']),
      include_package_data=True,
      package_data={'autocompleteusers': ['htdocs/css/*.css', 'htdocs/css/*.gif', 'htdocs/js/*.js']},
      zip_safe=False,
      entry_points="""
      [trac.plugins]
      autocompleteusers = autocompleteusers.autocompleteusers
      """,
)

