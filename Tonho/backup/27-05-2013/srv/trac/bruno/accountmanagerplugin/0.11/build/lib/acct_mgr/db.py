# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Matthew Good <trac@matt-good.net>
# Copyright (C) 2010-2012 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

from trac.core import Component, implements
from trac.config import ExtensionOption

from acct_mgr.api import IPasswordStore, _, N_
from acct_mgr.pwhash import IPasswordHashMethod


class SessionStore(Component):
    implements(IPasswordStore)

    hash_method = ExtensionOption('account-manager', 'hash_method',
        IPasswordHashMethod, 'HtDigestHashMethod',
        doc = N_("IPasswordHashMethod used to create new/updated passwords"))

    def __init__(self):
        self.key = 'password'
        # Check for valid hash method configuration.
        self.hash_method_enabled

    def get_users(self):
        """Returns an iterable of the known usernames."""
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT sid
            FROM    session_attribute
            WHERE   authenticated=1
                AND name=%s
            """, (self.key,))
        for sid, in cursor:
            yield sid
 
    def has_user(self, user):
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("""
            SELECT  *
            FROM    session_attribute
            WHERE   authenticated=1
                AND name=%s
                AND sid=%s
            """, (self.key, user))
        for row in cursor:
            return True
        return False

    def set_password(self, user, password, old_password=None):
        """Sets the password for the user.

        This should create the user account, if it doesn't already exist.
        Returns True, if a new account was created, and False,
        if an existing account was updated.
        """
        if not self.hash_method_enabled:
            return
        hash = self.hash_method.generate_hash(user, password)
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        sql = """
            WHERE   authenticated=1
                AND name=%s
                AND sid=%s
            """
        cursor.execute("""
            UPDATE  session_attribute
                SET value=%s
            """ + sql, (hash, self.key, user))
        cursor.execute("""
            SELECT  value
            FROM    session_attribute
            """ + sql, (self.key, user))
        not_exists = cursor.fetchone() is None
        if not_exists:
            cursor.execute("""
                INSERT INTO session_attribute
                        (sid,authenticated,name,value)
                VALUES  (%s,1,%s,%s)
                """, (user, self.key, hash))
        db.commit()
        return not_exists

    def check_password(self, user, password):
        """Checks if the password is valid for the user."""
        if not self.hash_method_enabled:
            return
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("""
            SELECT  value
            FROM    session_attribute
            WHERE   authenticated=1
                AND name=%s
                AND sid=%s
            """, (self.key, user))
        for hash, in cursor:
            return self.hash_method.check_hash(user, password, hash)
        # Return value 'None' allows to proceed with another, chained store.
        return

    def delete_user(self, user):
        """Deletes the user account.

        Returns True, if the account existed and was deleted, False otherwise.
        """
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        sql = """
            WHERE   authenticated=1
                AND name=%s
                AND sid=%s
            """
        # Avoid has_user() to make this transaction atomic.
        cursor.execute("""
            SELECT  *
            FROM    session_attribute
            """ + sql, (self.key, user))
        exists = cursor.fetchone() is not None
        if exists:
            cursor.execute("""
                DELETE
                FROM    session_attribute
                """ + sql, (self.key, user))
            db.commit()
        return exists

    @property
    def hash_method_enabled(self):
        try:
            hash_method = self.hash_method
        except AttributeError:
            self.env.log.error("%s: no IPasswordHashMethod enabled "
                               "- fatal, can't work" % self.__class__)
            return
        return True
