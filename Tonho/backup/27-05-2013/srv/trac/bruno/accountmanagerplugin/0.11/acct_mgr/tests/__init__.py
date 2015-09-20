# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

import doctest
import unittest
try:
    import twill, subprocess
    INCLUDE_FUNCTIONAL_TESTS = True
except ImportError:    
    INCLUDE_FUNCTIONAL_TESTS = False

def suite():
    from acct_mgr.tests import api, db, htfile, register
    suite = unittest.TestSuite()
    suite.addTest(api.suite())
    suite.addTest(db.suite())
    suite.addTest(htfile.suite())
    suite.addTest(register.suite())
    if INCLUDE_FUNCTIONAL_TESTS:
        from acct_mgr.tests.functional import suite as functional_suite
        suite.addTest(functional_suite())
    return suite

if __name__ == '__main__':
    import sys
    if '--skip-functional-tests' in sys.argv:
        sys.argv.remove('--skip-functional-tests')
        INCLUDE_FUNCTIONAL_TESTS = False
    unittest.main(defaultTest='suite')
