# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# Copyright (C) 2011 Dennis McRitchie
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

from urllib2 import build_opener, HTTPDigestAuthHandler, \
                    HTTPPasswordMgrWithDefaultRealm
from urlparse import urlparse

from trac.core import Component, implements
from trac.config import Option
from trac.web.href import Href

from acct_mgr.api import IPasswordStore, _, N_
from acct_mgr.util import HTTPBasicAuthHandler


class HttpAuthStore(Component):
    implements(IPasswordStore)

    auth_url = Option('account-manager', 'authentication_url', '',
        doc = N_("URL of the HTTP authentication service"))

    def check_password(self, username, password):
        self.log.debug("Trac.ini authentication_url = '%s'" % self.auth_url)
        # Nothing to do, if URL is absolute.
        if self.auth_url.startswith('http://') or \
                self.auth_url.startswith('https://'):
            authUrl = self.auth_url
        # Handle server-relative URLs.
        elif self.auth_url.startswith('/'):
            # Prepend the Trac server component.
            pr = urlparse(self.env.abs_href())
            href = Href(pr[0] + '://' + pr[1])
            authUrl = href(self.auth_url)
        elif '/' in self.auth_url:
            # URLs with path like 'common/authFile' or 'site/authFile'.
            authUrl = self.env.abs_href.chrome(self.auth_url)
        else:
            # Bare file name option value like 'authFile'.
            authUrl = self.env.abs_href.chrome('common', self.auth_url)
        self.log.debug("Final auth_url = '%s'" % authUrl)

        acctmgr = HTTPPasswordMgrWithDefaultRealm()
        acctmgr.add_password(None, authUrl, username, password)
        try:
            build_opener(HTTPBasicAuthHandler(acctmgr),
                         HTTPDigestAuthHandler(acctmgr)).open(authUrl)
        except IOError,e:
            if hasattr(e, 'code') and e.code == 404:
                self.log.debug("""HttpAuthStore page not found; we are
                               authenticated nonetheless""")
                return True
            if hasattr(e, 'code') and e.code == 401:
                self.log.debug("HttpAuthStore authentication failed")
            return None
        except ValueError, e:
            self.log.debug("""HttpAuthStore: 'authentication_url' specifies
                           an invalid URL""")
            return None
        else:
            self.log.debug("HttpAuthStore page exists; we are authenticated")
            return True

    def get_users(self):
        return []

    def has_user(self, user):
        return False
