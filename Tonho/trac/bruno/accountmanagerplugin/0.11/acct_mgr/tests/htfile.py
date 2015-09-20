# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# Copyright (C) 2011 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

import os.path
import shutil
import tempfile
import unittest

from trac.test import EnvironmentStub, Mock

from acct_mgr.htfile import HtDigestStore, HtPasswdStore

class _BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.env = EnvironmentStub()
        self.env.path = os.path.join(self.basedir, 'trac-tempenv')
        os.mkdir(self.env.path)

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def _create_file(self, *path, **kw):
        filename = os.path.join(self.basedir, *path)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        fd = file(filename, 'w')
        content = kw.get('content')
        if content is not None:
            fd.write(content)
        fd.close()
        return filename

    def _init_password_file(self, flavor, filename, content):
        filename = self._create_file(filename, content=content)
        self.env.config.set('account-manager', flavor + '_file', filename)

    def _do_password_test(self, flavor, filename, content):
        self._init_password_file(flavor, filename, content)
        self.assertTrue(self.store.check_password('user', 'password'))


class HtDigestTestCase(_BaseTestCase):
    def setUp(self):
        _BaseTestCase.setUp(self)
        self.env.config.set('account-manager', 'digest_password_store',
                            'HtDigestStore')
        self.env.config.set('account-manager', 'htdigest_realm',
                            'TestRealm')
        self.store = HtDigestStore(self.env)

    def test_userline(self):
        self.assertEqual(self.store.userline('user', 'password'),
                         'user:TestRealm:752b304cc7cf011d69ee9b79e2cd0866')

    def test_file(self):
        self._do_password_test('htdigest', 'test_file', 
                         'user:TestRealm:752b304cc7cf011d69ee9b79e2cd0866')

    def test_unicode(self):
        self.env.config.set('account-manager', 'htdigest_realm',
                            u'UnicodeRealm\u4e60')
        user = u'\u4e61'
        password = u'\u4e62'
        self._init_password_file('htdigest', 'test_unicode', '')
        self.store.set_password(user, password)
        self.assertEqual([user], list(self.store.get_users()))
        self.assertTrue(self.store.check_password(user, password))
        self.assertTrue(self.store.delete_user(user))
        self.assertEqual([], list(self.store.get_users()))

    def test_update_password(self):
        self._init_password_file('htdigest', 'test_passwdupd', '')
        self.store.set_password('foo', 'pass1')
        self.assertFalse(self.store.check_password('foo', 'pass2'))
        self.store.set_password('foo', 'pass2')
        self.assertTrue(self.store.check_password('foo', 'pass2'))
        self.store.set_password('foo', 'pass3', 'pass2')
        self.assertTrue(self.store.check_password('foo', 'pass3'))


class HtPasswdTestCase(_BaseTestCase):
    def setUp(self):
        _BaseTestCase.setUp(self)
        self.env.config.set('account-manager', 'htpasswd_store',
                            'HtPasswdStore')
        self.store = HtPasswdStore(self.env)

    def test_md5(self):
        self._do_password_test('htpasswd', 'test_md5',
                               'user:$apr1$xW/09...$fb150dT95SoL1HwXtHS/I0\n')

    def test_crypt(self):
        self._do_password_test('htpasswd', 'test_crypt',
                               'user:QdQ/xnl2v877c\n')

    def test_sha(self):
        self._do_password_test('htpasswd', 'test_sha',
                               'user:{SHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=\n')

    def test_sha256(self):
        self._do_password_test('htpasswd', 'test_sha256',
                               'user:$5$saltsaltsaltsalt$'
                               'WsFBeg1qQ90JL3VkUTuM7xVV/5njhLngIVm6ftSnBR2\n')

    def test_sha512(self):
        self._do_password_test('htpasswd', 'test_sha512',
                               'user:$6$saltsaltsaltsalt$'
                               'bcXJ8qxwY5sQ4v8MTl.0B1jeZ0z0JlA9jjmbUoCJZ.1'
                               'wYXiLTU.q2ILyrDJLm890lyfuF7sWAeli0yjOyFPkf0\n')

    def test_no_trailing_newline(self):
        self._do_password_test('htpasswd', 'test_no_trailing_newline',
                               'user:$apr1$xW/09...$fb150dT95SoL1HwXtHS/I0')

    def test_add_with_no_trailing_newline(self):
        filename = self._create_file('test_add_with_no_trailing_newline',
                                     content='user:$apr1$'
                                             'xW/09...$fb150dT95SoL1HwXtHS/I0')
        self.env.config.set('account-manager', 'htpasswd_file', filename)
        self.assertTrue(self.store.check_password('user', 'password'))
        self.store.set_password('user2', 'password2')
        self.assertTrue(self.store.check_password('user', 'password'))
        self.assertTrue(self.store.check_password('user2', 'password2'))

    def test_unicode(self):
        user = u'\u4e61'
        password = u'\u4e62'
        self._init_password_file('htpasswd', 'test_unicode', '')
        self.store.set_password(user, password)
        self.assertEqual([user], list(self.store.get_users()))
        self.assertTrue(self.store.check_password(user, password))
        self.assertTrue(self.store.delete_user(user))
        self.assertEqual([], list(self.store.get_users()))

    def test_update_password(self):
        self._init_password_file('htpasswd', 'test_passwdupd', '')
        self.store.set_password('foo', 'pass1')
        self.assertFalse(self.store.check_password('foo', 'pass2'))
        self.store.set_password('foo', 'pass2')
        self.assertTrue(self.store.check_password('foo', 'pass2'))
        self.store.set_password('foo', 'pass3', 'pass2')
        self.assertTrue(self.store.check_password('foo', 'pass3'))

    def test_create_hash(self):
        self._init_password_file('htpasswd', 'test_hash', '')
        self.env.config.set('account-manager', 'htpasswd_hash_type', 'bad')
        self.assertTrue(self.store.userline('user',
                                            'password').startswith('user:'))
        self.assertFalse(self.store.userline('user', 'password'
                                            ).startswith('user:$apr1$'))
        self.assertFalse(self.store.userline('user', 'password'
                                            ).startswith('user:{SHA}'))
        self.store.set_password('user', 'password')
        self.assertTrue(self.store.check_password('user', 'password'))
        self.env.config.set('account-manager', 'htpasswd_hash_type', 'md5')
        self.assertTrue(self.store.userline('user', 'password'
                                           ).startswith('user:$apr1$'))
        self.store.set_password('user', 'password')
        self.assertTrue(self.store.check_password('user', 'password'))
        self.env.config.set('account-manager', 'htpasswd_hash_type', 'sha')
        self.assertTrue(self.store.userline('user', 'password'
                                           ).startswith('user:{SHA}'))
        self.store.set_password('user', 'password')
        self.assertTrue(self.store.check_password('user', 'password'))
        self.env.config.set('account-manager', 'htpasswd_hash_type', 'sha256')
        self.assertTrue(self.store.userline('user', 'password'
                                           ).startswith('user:$5$'))
        self.store.set_password('user', 'password')
        self.assertTrue(self.store.check_password('user', 'password'))
        self.env.config.set('account-manager', 'htpasswd_hash_type', 'sha512')
        self.assertTrue(self.store.userline('user', 'password'
                                           ).startswith('user:$6$'))
        self.store.set_password('user', 'password')
        self.assertTrue(self.store.check_password('user', 'password'))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HtDigestTestCase, 'test'))
    suite.addTest(unittest.makeSuite(HtPasswdTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
