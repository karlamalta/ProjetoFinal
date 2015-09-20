# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

import os

from trac.core import Component, implements
from trac.config import Configuration
from trac.versioncontrol import RepositoryManager

from acct_mgr.api import IPasswordStore, _, N_
from acct_mgr.util import EnvRelativePathOption


class SvnServePasswordStore(Component):
    """PasswordStore implementation for reading svnserve's password file format
    """

    implements(IPasswordStore)

    filename = EnvRelativePathOption('account-manager', 'password_file',
        doc = N_("""Path to the users file; leave blank to locate
                the users file by reading svnserve.conf"""))

    def __init__(self):
        repo_dir = RepositoryManager(self.env).repository_dir
        self._svnserve_conf = Configuration(os.path.join(os.path.join(
                                  repo_dir, 'conf'), 'svnserve.conf'))
        self._userconf = None

    def _config(self):
        filename = self.filename
        if not filename:
            self._svnserve_conf.parse_if_needed()
            filename = self._svnserve_conf['general'].getpath('password-db')
        if self._userconf is None or filename != self._userconf.filename:
            self._userconf = Configuration(filename)
            # Overwrite default with str class to preserve case.
            self._userconf.parser.optionxform = str
            self._userconf.parse_if_needed(force=True)
        else:
            self._userconf.parse_if_needed()
        return self._userconf
    _config = property(_config)

    # IPasswordStore methods

    def get_users(self):
        return [user for (user,password) in self._config.options('users')]

    def has_user(self, user):
        return user in self._config['users']
 
    def set_password(self, user, password, old_password = None):
        cfg = self._config
        cfg.set('users', user, password)
        cfg.save()
 
    def check_password(self, user, password):
        if self.has_user(user):
            return password == self._config.get('users', user)
        return None

    def delete_user(self, user):
        cfg = self._config
        cfg.remove('users', user)
        cfg.save()
