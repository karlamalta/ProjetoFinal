# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# Copyright (C) 2010-2012 Steffen Hoffmann <hoff.st@web.de>
# Copyright (C) 2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

import os
import sys

from genshi.builder import tag

from trac.config import Option
from trac.util.datefmt import format_datetime, pretty_timedelta
from trac.web.chrome import Chrome

from acct_mgr.api import _


# Fix for issue http://bugs.python.org/issue8797 in Python 2.6
# following Bitten changeset 974.
if sys.version_info[:2] == (2, 6):
    import urllib2
    import base64

    class HTTPBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
        """Patched version of Python 2.6's HTTPBasicAuthHandler.
        
        The fix for [1]_ introduced an infinite recursion bug [2]_ into
        Python 2.6.x that is triggered by attempting to connect using
        Basic authentication with a bad username and/or password. This
        class fixes the problem using the simple solution outlined in [3]_.
        
        .. [1] http://bugs.python.org/issue3819
        .. [2] http://bugs.python.org/issue8797
        .. [3] http://bugs.python.org/issue8797#msg126657
        """

        def retry_http_basic_auth(self, host, req, realm):
            user, pw = self.passwd.find_user_password(realm, host)
            if pw is not None:
                raw = "%s:%s" % (user, pw)
                auth = 'Basic %s' % base64.b64encode(raw).strip()
                if req.get_header(self.auth_header, None) == auth:
                    return None
                req.add_unredirected_header(self.auth_header, auth)
                return self.parent.open(req, timeout=req.timeout)
            else:
                return None

else:
    from urllib2 import HTTPBasicAuthHandler


class EnvRelativePathOption(Option):

    def __get__(self, instance, owner):
        if instance is None:
            return self
        path = super(EnvRelativePathOption, self).__get__(instance, owner)
        if not path:
            return path
        return os.path.normpath(os.path.join(instance.env.path, path))

# taken from a comment of Horst Hansen
# at http://code.activestate.com/recipes/65441
def containsAny(str, set):
    for c in set:
        if c in str:
            return True
    return False

def if_enabled(func):
    def wrap(self, *args, **kwds):
        if not self.enabled:
            return None
        return func(self, *args, **kwds)
    return wrap

# Compatibility code for `ComponentManager.is_enabled`
# (available since Trac 0.12)
def is_enabled(env, cls):
    """Return whether the given component class is enabled.

    For Trac 0.11 the missing algorithm is included as fallback.
    """
    try:
        return env.is_enabled(cls)
    except AttributeError:
        if cls not in env.enabled:
            env.enabled[cls] = env.is_component_enabled(cls)
        return env.enabled[cls]

# Compatibility code for `pretty_dateinfo` from template data dict
# (available since Trac 0.13)
def get_pretty_dateinfo(env, req):
    """Return the function defined in trac.web.chrome.Chrome.populate_data .

    For Trac 0.11 and 0.12 it still provides a slightly simplified version.
    """
    # Function is not a class attribute, must be extracted from data dict.
    fn = Chrome(env).populate_data(req, {}).get('pretty_dateinfo')
    if not fn:
        def _pretty_dateinfo(date, format=None, dateonly=False):
            absolute = format_datetime(date, tzinfo=req.tz)
            relative = pretty_timedelta(date)
            if format == 'absolute':
                label = absolute
                # TRANSLATOR: Sync with same msgid in Trac 0.13, please.
                title = _("%(relativetime)s ago", relativetime=relative)
            else:
                if dateonly:
                    label = relative
                else:
                    label = _("%(relativetime)s ago", relativetime=relative)
                title = absolute
            return tag.span(label, title=title)
    return fn and fn or _pretty_dateinfo
