#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join as pathjoin
from setuptools import setup, find_packages

VERSION = "0.2.6"

try:
    LONG_DESCRIPTION = "".join([
        open("README.txt").read(),
        open("CHANGELOG.txt").read(),
    ])
except:
    LONG_DESCRIPTION = ""

REQUIRES = [
    "Trac >= 0.12",
]

CLASSIFIERS = [
    "Framework :: Trac",
    "Development Status :: 4 - Beta",
    "Environment :: Web Environment",
    "License :: OSI Approved :: Apache Software License",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development",
]

EXTRA_PARAMETER = {}
try:
    # Adding i18n/l10n to Trac plugins (Trac >= 0.12)
    # see also: http://trac.edgewall.org/wiki/CookBook/PluginL10N
    from trac.util.dist import get_l10n_cmdclass
    cmdclass = get_l10n_cmdclass()
    if cmdclass:  # Yay, Babel is there, we"ve got something to do!
        EXTRA_PARAMETER["cmdclass"] = cmdclass
        EXTRA_PARAMETER["message_extractors"] = {
            "ticketref": [
                ("**.py", "python", None),
            ]
        }
except ImportError:
    pass

setup(
    name="TracFeaturePlugin",
    version=VERSION,
    description="Provides support for feature reference in SPLIT.",
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=["trac", "plugin", "ticket", "cross-reference"],
    author="Bruno Cabral",
    author_email="bcabral@uw.edu",
    url="http://trac-hacks.org/wiki/TracTicketReferencePlugin",
    license="Apache License 2.0",
    packages=["ticketref"],
    package_data={
        "ticketref": [
            "htdocs/*.js",
            "htdocs/*.css",
            "locale/*/LC_MESSAGES/*.po",
            "locale/*/LC_MESSAGES/*.mo",
        ],
    },
    include_package_data=True,
    install_requires=REQUIRES,
    entry_points={
        "trac.plugins": [
            "ticketref.web_ui = ticketref.web_ui",
            "ticketref.api = ticketref.api",
        ]
    },
    **EXTRA_PARAMETER
)
