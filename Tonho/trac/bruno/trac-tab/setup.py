#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Bobby Smith <bobbysmith007@gmail.com>
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

from setuptools import setup

setup(name='TracTab',
      version='0.2.0',
      license='BSD 2-Clause',
      author='Bobby Smith',
      author_email='bobbysmith007@gmail.com',
      maintainer='Ryan J Ollos',
      maintainer_email='ryan.j.ollos.@gmail.com',
      description="Add a button to the mainnav and display a page within"
                  "an IFrame",
      longdescription="""
      This plugin allows you to add a button to the main navigation bar
      and serve a page in the Trac template within an Iframe linking
      to the appropriate URL. This will work for any number of URLs
      specified in the proper format.""",
      url='http://trac-hacks.org/svn/tractabplugin',
      packages=['tractab'],
      package_data={'tractab' : ['templates/*.html']},
      entry_points={'trac.plugins': 'tractab = tractab.tractab'},
)

