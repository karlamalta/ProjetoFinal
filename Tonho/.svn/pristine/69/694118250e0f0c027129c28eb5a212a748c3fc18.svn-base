# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Steffen Hoffmann <hoff.st@web.de>

import shutil
import string
import tempfile
import unittest

from Cookie  import SimpleCookie as Cookie
from genshi.core  import Markup

from trac.perm  import PermissionCache, PermissionSystem
from trac.test  import EnvironmentStub, Mock, MockPerm
from trac.web.session  import Session

from acct_mgr.api  import AccountManager, IAccountRegistrationInspector
from acct_mgr.db  import SessionStore
from acct_mgr.htfile  import HtPasswdStore
from acct_mgr.model  import set_user_attribute
from acct_mgr.register  import BasicCheck, BotTrapCheck, EmailCheck, \
                               EmailVerificationModule, \
                               GenericRegistrationInspector, RegExpCheck, \
                               RegistrationError, RegistrationModule, \
                               UsernamePermCheck


class _BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentStub(
                enable=['trac.*', 'acct_mgr.api.*'])
        self.env.path = tempfile.mkdtemp()
        self.perm = PermissionSystem(self.env)

        # Create a user reference in the permission system.
        self.perm.grant_permission('admin', 'ACCTMGR_USER_ADMIN')
        # Prepare a generic registration request.
        args = dict(username='', name='', email='')
        self.req = Mock(authname='anonymous', args=args)
        self.req.perm = PermissionCache(self.env)

    def tearDown(self):
        shutil.rmtree(self.env.path)


class DummyRegInspectorTestCase(_BaseTestCase):
    """Check GenericRegistrationInspector properties via child classes."""
    def setUp(self):
        _BaseTestCase.setUp(self)

        class DummyRegistrationInspector(GenericRegistrationInspector):
            def validate_registration(self, req):
                if req.args.get('username') == 'dummy':
                    raise RegistrationError('Dummy check error')
                return

        self.check = DummyRegistrationInspector(self.env)

    def test_bad_check(self):
        class BadRegistrationInspector(GenericRegistrationInspector):
            """Child class, that is left as a pure copy of its base.

            Bad check class example, because check method is not implemented.
            """

        check = BadRegistrationInspector(self.env)
        # Default (empty) response for providing additional fields is safe.
        field_res = check.render_registration_fields(self.req, {})
        self.assertEqual(len(field_res), 2)
        self.assertEqual((Markup(field_res[0]), field_res[1]),
                         (Markup(''), {}))
        # Check class without 'validate_registration' implementation fails.
        self.assertRaises(NotImplementedError, check.validate_registration,
                          self.req)

    def test_dummy_check(self):
        # Check class with 'validate_registration' passes this test.
        self.assertEqual(self.check.validate_registration(self.req), None)

    def test_check_error(self):
        self.req.args['username'] = 'dummy'
        try:
            self.check.validate_registration(self.req)
            # Shouldn't reach that point.
            self.assertTrue(False)
        except RegistrationError, e:
            # Check error properties in detail.
            self.assertEqual(e.message, 'Dummy check error')
            self.assertEqual(e.title, 'Registration Error')


class BasicCheckTestCase(_BaseTestCase):
    def setUp(self):
        _BaseTestCase.setUp(self)
        self.env = EnvironmentStub(
                enable=['trac.*', 'acct_mgr.admin.*',
                        'acct_mgr.pwhash.HtDigestHashMethod'])
        self.env.path = tempfile.mkdtemp()
        self.env.config.set('account-manager', 'password_store',
                            'SessionStore')
        store = SessionStore(self.env)
        store.set_password('registered_user', 'password')

    def test_check(self):
        check = BasicCheck(self.env)
        req = self.req
        # Inspector doesn't provide additional fields.
        field_res = check.render_registration_fields(req, {})
        self.assertEqual(len(field_res), 2)
        self.assertEqual((Markup(field_res[0]), field_res[1]),
                         (Markup(''), {}))
        # 1st attempt: No input.
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 2nd attempt: Illegal character.
        req.args['username'] = 'user:name'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 3rd attempt: All upper-case word.
        req.args['username'] = 'UPPER-CASE_USER'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 4th attempt: Reserved word.
        req.args['username'] = 'Anonymous'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 5th attempt: Existing user.
        req.args['username'] = 'registered_user'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 6th attempt: Valid username, but no password.
        req.args['username'] = 'user'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 7th attempt: Valid username, no matching passwords.
        req.args['password'] = 'password'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 8th attempt: Finally some valid input.
        req.args['password_confirm'] = 'password'
        self.assertEqual(check.validate_registration(req), None)


class BotTrapCheckTestCase(_BaseTestCase):
    def setUp(self):
        _BaseTestCase.setUp(self)
        self.basic_token = "Yes, I'm human"
        self.env.config.set('account-manager', 'register_basic_token',
                            self.basic_token)

    def test_check(self):
        check = BotTrapCheck(self.env)
        req = self.req

        # Inspector provides the email text input field.
        wrong_input = "Hey, I'm a bot."
        data = dict(basic_token=wrong_input)
        req.args.update(data)
        field_res = check.render_registration_fields(req, data)
        self.assertEqual(len(field_res), 2)
        self.assertTrue(Markup(field_res[0]).startswith('<label>Parole:'))

        # 1st attempt: Wrong input.
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # Ensure, that old input is restored on failure.
        self.assertTrue(wrong_input in Markup(field_res[0]))
        # Ensure, that template data dict is passed unchanged.
        self.assertEqual(field_res[1], data)

        # 2nd attempt: No input.
        req.args['basic_token'] = ''
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 3th attempt: Finally valid input.
        req.args['basic_token'] = self.basic_token
        self.assertEqual(check.validate_registration(req), None)
        # 4rd attempt: Fill the hidden field too.
        req.args['sentinel'] = "Humans can't see this? Crap - I'm superior!"
        self.assertRaises(RegistrationError, check.validate_registration, req)


class EmailCheckTestCase(_BaseTestCase):
    """Needs several test methods, because dis-/enabling a component doesn't
    work within one method.
    """

    def test_verify_mod_disabled(self):
        """Registration challenges with EmailVerificationModule disabled."""
        self.env = EnvironmentStub(
                enable=['trac.*', 'acct_mgr.admin.*'])
        self.env.path = tempfile.mkdtemp()

        check = EmailCheck(self.env)
        req = self.req

        self.env.config.set('account-manager', 'verify_email', False)
        self.assertEqual(check.validate_registration(req), None)
        # Check should be skipped regardless of AccountManager settings.
        self.env.config.set('account-manager', 'verify_email', True)
        self.assertEqual(check.validate_registration(req), None)

    def test_verify_conf_changes(self):
        """Registration challenges with EmailVerificationModule enabled."""
        self.env = EnvironmentStub(
                enable=['trac.*', 'acct_mgr.admin.*', 'acct_mgr.register.*'])
        self.env.path = tempfile.mkdtemp()
        set_user_attribute(self.env, 'admin', 'email', 'admin@foo.bar')

        check = EmailCheck(self.env)
        req = self.req

        # Inspector provides the email text input field.
        old_email_input = 'email@foo.bar'
        acct = dict(username='user', email=old_email_input, name='User')
        req.args.update(acct)
        field_res = check.render_registration_fields(req, acct)
        self.assertEqual(len(field_res), 2)
        self.assertTrue(Markup(field_res[0]).startswith('<label>Email:'))
        # Ensure, that old input is restored on failure.
        self.assertTrue(old_email_input in Markup(field_res[0]))
        # Ensure, that template data dict is passed unchanged.
        self.assertEqual(field_res[1], acct)
        req.args.update(dict(email=''))

        # 1st: Initially try with account verification disabled by setting.
        self.env.config.set('account-manager', 'verify_email', False)
        self.assertEqual(check.validate_registration(req), None)
        # 2nd: Again no email, but now with account verification enabled. 
        self.env.config.set('account-manager', 'verify_email', True)
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 3th attempt: Valid email, but already registered with a username.
        req.args['email'] = 'admin@foo.bar'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 4th attempt: Finally some valid input.
        req.args['email'] = 'email@foo.bar'
        self.assertEqual(check.validate_registration(req), None)


class RegExpCheckTestCase(_BaseTestCase):
    def test_check(self):
        self.env = EnvironmentStub(
                enable=['trac.*', 'acct_mgr.admin.*', 'acct_mgr.register.*'])
        self.env.path = tempfile.mkdtemp()

        check = RegExpCheck(self.env)
        req = self.req
        # Inspector doesn't provide additional fields.
        field_res = check.render_registration_fields(req, {})
        self.assertEqual(len(field_res), 2)
        self.assertEqual((Markup(field_res[0]), field_res[1]),
                         (Markup(''), {}))
        # Empty input is invalid with default regular expressions.
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 1st attempt: Malformed email address.
        req.args['username'] = 'username'
        req.args['email'] = 'email'
        self.assertRaises(RegistrationError, check.validate_registration,
                          req)
        # 2nd attempt: Same as before, but with email verification disabled.
        self.env.config.set('account-manager', 'verify_email', False)
        self.assertEqual(check.validate_registration(req), None)
        # 3rd attempt: Now with email verification enabled, but valid email.
        self.env.config.set('account-manager', 'verify_email', True)
        req.args['email'] = 'email@foo.bar'
        self.assertEqual(check.validate_registration(req), None)
        # 4th attempt: Now with too short username.
        req.args['username'] = 'user'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 5th attempt: Allow short username by custom regular expression.
        self.env.config.set('account-manager', 'username_regexp',
                            r'(?i)^[A-Z.\-_]{4,}$')
        self.assertEqual(check.validate_registration(req), None)
        # 6th attempt: Now with username containing single quote.
        req.args['username'] = 'user\'name'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 7th attempt: Alter config to allow username containing single quote.
        self.env.config.set('account-manager', 'username_regexp',
                            r'(?i)^[A-Z.\-\'_]{4,}$')
        self.assertEqual(check.validate_registration(req), None)


class UsernamePermCheckTestCase(_BaseTestCase):
    def test_check(self):
        check = UsernamePermCheck(self.env)
        req = self.req
        # Inspector doesn't provide additional fields.
        field_res = check.render_registration_fields(req, {})
        self.assertEqual(len(field_res), 2)
        self.assertEqual((Markup(field_res[0]), field_res[1]),
                         (Markup(''), {}))
        # 1st attempt: No username, hence no conflic possible.
        self.assertEqual(check.validate_registration(req), None)
        # 2nd attempt: No permission assigned for that username.
        req.args['username'] = 'user'
        self.assertEqual(check.validate_registration(req), None)
        # 3rd attempt: Explicite permission assigned for that username.
        req.args['username'] = 'admin'
        self.assertRaises(RegistrationError, check.validate_registration, req)
        # 4th attempt: As before, but request done by admin user.
        req.perm = PermissionCache(self.env, 'admin')
        self.assertEqual(check.validate_registration(req), None)


class RegistrationModuleTestCase(_BaseTestCase):
    def setUp(self):
        _BaseTestCase.setUp(self)
        self.env = EnvironmentStub(enable=[
                       'trac.*', 'acct_mgr.api.*', 'acct_mgr.db.*',
                       'acct_mgr.register.*',
                       'acct_mgr.pwhash.HtDigestHashMethod'
                   ])
        self.env.path = tempfile.mkdtemp()
        self.reg_template = 'register.html'
        self.req.method = 'POST'

        self.env.config.set('account-manager', 'password_store',
                            'SessionStore')
        self.acctmgr = AccountManager(self.env)
        self.check = BasicCheck(self.env)
        self.rmod = RegistrationModule(self.env)
        self.store = SessionStore(self.env)

    def test_checks(self):
        # Default configuration: All default checks enabled.
        response = self.rmod.process_request(self.req)
        self.assertEqual(response[0], self.reg_template)

        # Custom configuration: Do basic username checks only.
        self.req.args['username'] = 'admin'
        self.req.args['email'] = 'admin@foo.bar'
        self.env.config.set('account-manager', 'register_check',
                            'BasicCheck')
        response = self.rmod.process_request(self.req)
        self.assertEqual(response[0], self.reg_template)

        # Custom configuration: No check at all, if you insist.
        self.env.config.set('account-manager', 'register_check', '')
        self.assertFalse(self.acctmgr._register_check)
        response = self.rmod.process_request(self.req)
        self.assertEqual(response[0], self.reg_template)

    def test_mandatory_email_registration(self):
        user = 'user1'
        passwd = 'test'
        # A more complete mock of a request object is required for this test.
        req = Mock(authname='anonymous', method='POST',
                   args={
                       'action': 'create',
                       'username': user,
                       'name': 'Tester',
                       'password': passwd,
                       'password_confirm': passwd
                   },
                   chrome=dict(notices=[], warnings=[]),
                   href=self.env.abs_href, perm=MockPerm(),
                   redirect=lambda x: None
        )
        # Fail to register the user.
        self.rmod.process_request(req)
        self.assertTrue('email address' in str(req.chrome['warnings']))
        self.assertEqual(list(self.store.get_users()), [])

    def test_optional_email_registration(self):
        user = 'user1'
        passwd = 'test'
        def redirect_noop(href):
            """Log relevant information for checking registration result."""
            #print req.chrome['notices']
            return
        # A more complete mock of a request object is required for this test.
        req = Mock(authname='anonymous', method='POST',
                   args={
                       'action': 'create',
                       'username': user,
                       'name': 'Tester',
                       'password': passwd,
                       'password_confirm': passwd
                   },
                   chrome=dict(notices=[], warnings=[]),
                   href=self.env.abs_href, perm=MockPerm(),
                   redirect=redirect_noop
        )
        self.env.config.set('account-manager', 'verify_email', False)
        # Successfully register the user.
        # Note: This would have raised an AttributeError without graceful
        #   request checking for 'email'.
        self.rmod.process_request(req)
        # DEVEL: Check registration success more directly.
        self.assertEqual(req.chrome['warnings'], [])
        self.assertEqual([user], list(self.store.get_users()))
        self.assertTrue(self.store.check_password(user, passwd))


class EmailVerificationModuleTestCase(_BaseTestCase):
    """Verify email address validation when running account verification."""
    def setUp(self):
        _BaseTestCase.setUp(self)
        self.env = EnvironmentStub(
                enable=['trac.*', 'acct_mgr.api.*', 'acct_mgr.register.*'])
        self.env.path = tempfile.mkdtemp()

        args = dict(username='user', name='', email='')
        incookie = Cookie()
        incookie['trac_session'] = '123456'
        self.req = Mock(authname='user', args=args, base_path='/',
                        chrome=dict(warnings=list()),
                        href=Mock(prefs=lambda x: None),
                        incookie=incookie, outcookie=Cookie(),
                        redirect=lambda x: None)
        self.req.method = 'POST'
        self.req.path_info = '/prefs'
        self.req.session = Session(self.env, self.req)
        self.req.session['email'] = 'email@foo.bar'
        self.req.session.save()
        self.vmod = EmailVerificationModule(self.env)

    def test_check_email_used(self):
        set_user_attribute(self.env, 'admin', 'email', 'admin@foo.bar')
        # Try email, that is already associated to another user.
        self.req.args['email'] = 'admin@foo.bar'
        self.vmod.pre_process_request(self.req, None)
        warnings = self.req.chrome.get('warnings')
        self.assertTrue(string.find(str(warnings and warnings[0] or ''),
                                    'already in use') > 0)

    def test_check_no_email(self):
        self.vmod.pre_process_request(self.req, None)
        warnings = self.req.chrome.get('warnings')
        self.assertNotEqual(str(warnings and warnings[0] or ''), '')

    def test_check(self):
        self.req.args['email'] = 'user@foo.bar'
        self.vmod.pre_process_request(self.req, None)
        warnings = self.req.chrome.get('warnings')
        self.assertEqual(str(warnings and warnings[0] or ''), '')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DummyRegInspectorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(BasicCheckTestCase, 'test'))
    suite.addTest(unittest.makeSuite(BotTrapCheckTestCase, 'test'))
    suite.addTest(unittest.makeSuite(EmailCheckTestCase, 'test'))
    suite.addTest(unittest.makeSuite(RegExpCheckTestCase, 'test'))
    suite.addTest(unittest.makeSuite(UsernamePermCheckTestCase, 'test'))
    suite.addTest(unittest.makeSuite(RegistrationModuleTestCase, 'test'))
    suite.addTest(unittest.makeSuite(EmailVerificationModuleTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
