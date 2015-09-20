# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# Copyright (C) 2010-2013 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

import random
import string
import time

from datetime import timedelta
from genshi.core import Markup
from genshi.builder import tag

from trac import perm, util
from trac.core import Component, implements
from trac.config import Configuration, BoolOption, IntOption, Option
from trac.env import open_environment
from trac.prefs import IPreferencePanelProvider
from trac.util import hex_entropy
from trac.util.presentation import separated
from trac.util.text import to_unicode
from trac.web import auth, chrome
from trac.web.main import IRequestHandler, IRequestFilter, get_environments
from trac.web.chrome import INavigationContributor, add_script, add_stylesheet

from acct_mgr.api import AccountManager, CommonTemplateProvider, \
                         _, dgettext, ngettext, tag_
from acct_mgr.db import SessionStore
from acct_mgr.guard import AccountGuard
from acct_mgr.model import set_user_attribute, user_known
from acct_mgr.register import EmailVerificationModule, RegistrationModule
from acct_mgr.util import if_enabled, is_enabled


class ResetPwStore(SessionStore):
    """User password store for the 'lost password' procedure."""
    def __init__(self):
        self.key = 'password_reset'


class AccountModule(CommonTemplateProvider):
    """Exposes methods for users to do account management on their own.

    Allows users to change their password, reset their password, if they've
    forgotten it, even delete their account.  The settings for the
    AccountManager module must be set in trac.ini in order to use this.
    Password reset procedure depends on both, ResetPwStore and an
    IPasswordHashMethod implementation being enabled as well.
    """

    implements(IPreferencePanelProvider, IRequestHandler,
               INavigationContributor, IRequestFilter)

    _password_chars = string.ascii_letters + string.digits
    password_length = IntOption(
        'account-manager', 'generated_password_length', 8,
        """Length of the randomly-generated passwords created when resetting
        the password for an account.""")

    reset_password = BoolOption(
        'account-manager', 'reset_password', True,
        'Set to False, if there is no email system setup.')

    def __init__(self):
        self.acctmgr = AccountManager(self.env)
        self.store = ResetPwStore(self.env)
        self._write_check(log=True)

    def _write_check(self, log=False):
        writable = self.acctmgr.get_all_supporting_stores('set_password')
        if not writable and log:
            self.log.warn("AccountModule is disabled because the password "
                          "store does not support writing.")
        return writable

    # IPreferencePanelProvider methods

    def get_preference_panels(self, req):
        writable = self._write_check()
        if not writable:
            return
        if req.authname and req.authname != 'anonymous':
            user_store = self.acctmgr.find_user_store(req.authname)
            if user_store in writable:
                yield 'account', _("Account")

    def render_preference_panel(self, req, panel):
        data = {'account': self._do_account(req),
                '_dgettext': dgettext,
               }
        return 'prefs_account.html', data

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == '/reset_password' and \
               self._reset_password_enabled(log=True)

    def process_request(self, req):
        data = {'_dgettext': dgettext,
                'reset': self._do_reset_password(req)
               }
        return 'reset_password.html', data, None

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        if req.path_info == '/prefs/account' and \
                not (req.authname and req.authname != 'anonymous'):
            # An anonymous session has no account associated with it, and
            # no account properies too, but general session preferences should
            # always be available.
            req.redirect(req.href.prefs())
        return handler

    def post_process_request(self, req, template, data, content_type):
        if req.authname and req.authname != 'anonymous':
            if req.session.get('force_change_passwd', False):
                redirect_url = req.href.prefs('account')
                if req.href(req.path_info) != redirect_url:
                    req.redirect(redirect_url)
        return (template, data, content_type)

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'reset_password'

    def get_navigation_items(self, req):
        if not self.reset_password_enabled or LoginModule(self.env).enabled:
            return
        if req.authname == 'anonymous':
            yield 'metanav', 'reset_password', tag.a(
                _("Forgot your password?"), href=req.href.reset_password())

    def _reset_password_enabled(self, log=False):
        try:
            self.store.hash_method
        except AttributeError:
            return False
        return is_enabled(self.env, self.__class__) and \
               self.reset_password and (self._write_check(log) != []) and \
               is_enabled(self.env, self.store.__class__) and \
               self.store.hash_method and True or False

    reset_password_enabled = property(_reset_password_enabled)

    def _do_account(self, req):
        assert(req.authname and req.authname != 'anonymous')
        action = req.args.get('action')
        delete_enabled = self.acctmgr.supports('delete_user') and \
                             self.acctmgr.allow_delete_account
        data = {'delete_enabled': delete_enabled,
                'delete_msg_confirm': _(
                    "Are you sure you want to delete your account?"),
               }
        force_change_password = req.session.get('force_change_passwd', False)
        if req.method == 'POST':
            if action == 'save':
                data.update(self._do_change_password(req))
                if 'message' in data and force_change_password:
                    del(req.session['force_change_passwd'])
                    req.session.save()
                    chrome.add_notice(req, Markup(tag.span(tag_(
                        "Thank you for taking the time to update your password."
                    ))))
                    force_change_password = False
            elif action == 'delete' and delete_enabled:
                data.update(self._do_delete(req))
            else:
                data.update({'error': 'Invalid action'})
        if force_change_password:
            chrome.add_warning(req, Markup(tag.span(_(
                "You are required to change password because of a recent "
                "password change request. "),
                tag.b(_("Please change your password now.")))))
        return data

    def _do_reset_password(self, req):
        if req.authname and req.authname != 'anonymous':
            return {'logged_in': True}
        if req.method != 'POST':
            return {}
        username = req.args.get('username')
        email = req.args.get('email')
        if not username:
            return {'error': _("Username is required")}
        if not email:
            return {'error': _("Email is required")}
        for username_, name, email_ in self.env.get_known_users():
            if username_ == username and email_ == email:
                error = self._reset_password(username, email)
                return error and error or {'sent_to_email': email}
        return {'error': _(
            "The email and username must match a known account.")}

    def _reset_password(self, username, email):
        acctmgr = self.acctmgr
        new_password = self._random_password()
        try:
            self.store.set_password(username, new_password)
            acctmgr._notify('password_reset', username, email, new_password)
        except Exception, e:
            return {'error': ','.join(map(to_unicode, e.args))}
        if acctmgr.force_passwd_change:
            set_user_attribute(self.env, username, 'force_change_passwd', 1)

    def _random_password(self):
        return ''.join([random.choice(self._password_chars)
                        for _ in xrange(self.password_length)])

    def _do_change_password(self, req):
        user = req.authname

        old_password = req.args.get('old_password')
        if not self.acctmgr.check_password(user, old_password):
            if not old_password:
                return {'save_error': _("Old password cannot be empty.")}
            return {'save_error': _("Old password is incorrect.")}

        password = req.args.get('password')
        if not password:
            return {'save_error': _("Password cannot be empty.")}
        if password != req.args.get('password_confirm'):
            return {'save_error': _("The passwords must match.")}
        if password == old_password:
            return {'save_error': _("Password must not match old password.")}

        self.acctmgr.set_password(user, password, old_password)
        if req.session.get('password') is not None:
            # Fetch all session_attributes in case new user password is in
            # SessionStore, to prevent unintended overwrite by session.save().
            req.session.get_session(req.authname, authenticated=True)
        return {'message': _("Password successfully updated.")}

    def _do_delete(self, req):
        user = req.authname

        password = req.args.get('password')
        if not password:
            return {'delete_error': _("Password cannot be empty.")}
        if not self.acctmgr.check_password(user, password):
            return {'delete_error': _("Password is incorrect.")}

        self.acctmgr.delete_user(user)
        # Delete the whole session since records in session_attribute would
        # get restored on logout otherwise.
        req.session.clear()
        req.session.save()
        req.redirect(req.href.logout())


class LoginModule(auth.LoginModule, CommonTemplateProvider):
    """Custom login form and processing.

    This is woven with the trac.auth.LoginModule it inherits and overwrites.
    But both can't co-exist, so Trac's built-in authentication module
    must be disabled to use this one.
    """

    # Trac core options, replicated here to not make them disappear by
    # disabling auth.LoginModule.
    check_ip = BoolOption('trac', 'check_auth_ip', 'false',
         """Whether the IP address of the user should be checked for
         authentication (''since 0.9'').""")

    ignore_case = BoolOption('trac', 'ignore_auth_case', 'false',
        """Whether login names should be converted to lower case
        (''since 0.9'').""")

    auth_cookie_lifetime = IntOption('trac', 'auth_cookie_lifetime', 0,
        """Lifetime of the authentication cookie, in seconds.
        
        This value determines how long the browser will cache
        authentication information, and therefore, after how much
        inactivity a user will have to log in again. The default value
        of 0 makes the cookie expire at the end of the browsing
        session. (''since 0.12'')""")

    auth_cookie_path = Option('trac', 'auth_cookie_path', '',
        """Path for the authentication cookie. Set this to the common
        base path of several Trac instances if you want them to share
        the cookie.  (''since 0.12'')""")

    # Options dedicated to acct_mgr.web_ui.LoginModule. 
    login_opt_list = BoolOption(
        'account-manager', 'login_opt_list', False,
        """Set to True, to switch login page style showing alternative actions
        in a single listing together.""")

    cookie_refresh_pct = IntOption(
        'account-manager', 'cookie_refresh_pct', 10,
        """Persistent sessions randomly get a new session cookie ID with
        likelihood in percent per work hour given here (zero equals to never)
        to decrease vulnerability of long-lasting sessions.""")

    environ_auth_overwrite = BoolOption(
        'account-manager', 'environ_auth_overwrite', True,
        """Whether environment variable REMOTE_USER should get overwritten after processing login
        form input. Otherwise it will only be set, if unset at the time of authentication.""")

    # Update cookies for persistant sessions only 1/day.
    #   hex_entropy returns 32 chars per call equal to 128 bit of entropy,
    #   so it should be technically impossible to explore the hash even within
    #   a year by just throwing forged HTTP requests at the server.
    #   I.e. it would require 1.000.000 machines, each at 5*10^24 requests/s,
    #   equal to a full-scale DDoS attack - an entirely different issue.
    UPDATE_INTERVAL = 86400

    def __init__(self):
        c = self.config
        if is_enabled(self.env, self.__class__) and \
                is_enabled(self.env, auth.LoginModule):
            # Disable auth.LoginModule to handle login requests alone.
            self.env.log.info("Concurrent enabled login modules found, "
                              "fixing configuration ...")
            c.set('components', 'trac.web.auth.loginmodule', 'disabled')
            c.save()
            self.env.log.info("trac.web.auth.LoginModule disabled, "
                              "giving preference to %s." % self.__class__)

        self.cookie_lifetime = self.auth_cookie_lifetime
        if not self.cookie_lifetime > 0:
            # Set the session to expire after some time and not
            #   when the browser is closed - what is Trac core default).
            self.cookie_lifetime = 86400 * 30   # AcctMgr default = 30 days
        self.auth_share_participants = []

    def authenticate(self, req):
        if req.method == 'POST' and req.path_info.startswith('/login') and \
                req.args.get('user_locked') is None:
            user = self._remote_user(req)
            acctmgr = AccountManager(self.env)
            guard = AccountGuard(self.env)
            if guard.login_attempt_max_count > 0:
                if user is None:
                    # Get user for failed authentication attempt.
                    f_user = req.args.get('user')
                    req.args['user_locked'] = False
                    # Log current failed login attempt.
                    guard.failed_count(f_user, req.remote_addr)
                    if guard.user_locked(f_user):
                        # Step up lock time prolongation only while locked.
                        guard.lock_count(f_user, 'up')
                        req.args['user_locked'] = True
                elif guard.user_locked(user):
                    req.args['user_locked'] = True
                    # Void successful login as long as user is locked.
                    user = None
                else:
                    req.args['user_locked'] = False
                    if req.args.get('failed_logins') is None:
                        # Reset failed login attempts counter.
                        req.args['failed_logins'] = guard.failed_count(user,
                                                                 reset=True)
            else:
                req.args['user_locked'] = False
            if not 'REMOTE_USER' in req.environ or self.environ_auth_overwrite:
                if 'REMOTE_USER' in req.environ:
                    # Complain about another component setting environment
                    # variable for authenticated user.
                    self.env.log.warn("LoginModule.authenticate: "
                                      "'REMOTE_USER' was set to '%s'"
                                      % req.environ['REMOTE_USER'])
                self.env.log.debug("LoginModule.authenticate: Set "
                                   "'REMOTE_USER' = '%s'" % user)
                req.environ['REMOTE_USER'] = user
        return auth.LoginModule.authenticate(self, req)

    authenticate = if_enabled(authenticate)

    match_request = if_enabled(auth.LoginModule.match_request)

    def process_request(self, req):
        if req.path_info.startswith('/login') and req.authname == 'anonymous':
            try:
                referer = self._referer(req)
            except AttributeError:
                # Fallback for Trac 0.11 compatibility.
                referer = req.get_header('Referer')
            # Steer clear of requests going nowhere or loop to self.
            if referer is None or \
                    referer.startswith(str(req.abs_href()) + '/login'):
                referer = req.abs_href()
            data = {
                '_dgettext': dgettext,
                'login_opt_list': self.login_opt_list,
                'persistent_sessions': AccountManager(self.env
                                       ).persistent_sessions,
                'referer': referer,
                'registration_enabled': RegistrationModule(self.env).enabled,
                'reset_password_enabled': AccountModule(self.env
                                          ).reset_password_enabled
            }
            if req.method == 'POST':
                self.log.debug(
                    "LoginModule.process_request: 'user_locked' = %s"
                    % req.args.get('user_locked'))
                if not req.args.get('user_locked'):
                    # TRANSLATOR: Intentionally obfuscated login error
                    data['login_error'] = _("Invalid username or password")
                else:
                    f_user = req.args.get('user')
                    release_time = AccountGuard(self.env
                                   ).pretty_release_time(req, f_user)
                    if not release_time is None:
                        data['login_error'] = _(
                            """Account locked, please try again after
                            %(release_time)s
                            """, release_time=release_time)
                    else:
                        data['login_error'] = _("Account locked")
            return 'login.html', data, None
        else:
            n_plural=req.args.get('failed_logins')
            if n_plural > 0:
                chrome.add_warning(req, Markup(tag.span(tag(ngettext(
                    "Login after %(attempts)s failed attempt",
                    "Login after %(attempts)s failed attempts",
                    n_plural, attempts=n_plural
                )))))
        return auth.LoginModule.process_request(self, req)

    # overrides
    def _get_name_for_cookie(self, req, cookie):
        """Returns the user name for the current Trac session.

        It's called by authenticate() when the cookie 'trac_auth' is sent
        by the browser.
        """

        acctmgr = AccountManager(self.env)

        # Disable IP checking when a persistent session is available, as the
        # user may have a dynamic IP adress and this would lead to the user 
        # being logged out due to an IP address conflict.
        checkIPSetting = self.check_ip and acctmgr.persistent_sessions and \
                         'trac_auth_session' in req.incookie
        if checkIPSetting:
            self.env.config.set('trac', 'check_auth_ip', False)
        
        name = auth.LoginModule._get_name_for_cookie(self, req, cookie)
        
        if checkIPSetting:
            # Re-enable IP checking
            self.env.config.set('trac', 'check_auth_ip', True)
        
        if acctmgr.persistent_sessions and name and \
                'trac_auth_session' in req.incookie and \
                int(req.incookie['trac_auth_session'].value) < \
                int(time.time()) - self.UPDATE_INTERVAL:
            # Persistent sessions enabled, the user is logged in
            # ('name' exists) and has actually decided to use this feature
            # (indicated by the 'trac_auth_session' cookie existing).
            # 
            # NOTE: This method is called on every request.
            
            # Refresh session cookie
            # Update the timestamp of the session so that it doesn't expire.
            self.env.log.debug('Updating session %s for user %s' %
                                (cookie.value, name))
            # Refresh in database
            db = self.env.get_db_cnx()
            cursor = db.cursor()
            cursor.execute("""
                UPDATE  auth_cookie
                    SET time=%s
                WHERE   cookie=%s
                """, (int(time.time()), cookie.value))
            db.commit()

            # Change session ID (cookie.value) now and then as it otherwise
            #   never would change at all (i.e. stay the same indefinitely and
            #   therefore is more vulnerable to be hacked).
            if random.random() + self.cookie_refresh_pct / 100.0 > 1:
                old_cookie = cookie.value
                # Update auth cookie value
                cookie.value = hex_entropy()
                self.env.log.debug('Changing session id for user %s to %s'
                                    % (name, cookie.value))
                db = self.env.get_db_cnx()
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE  auth_cookie
                        SET cookie=%s
                    WHERE   cookie=%s
                    """, (cookie.value, old_cookie))
                db.commit()
                self._distribute_cookie(req, cookie.value)

            cookie_lifetime = self.cookie_lifetime
            cookie_path = self._get_cookie_path(req)
            req.outcookie['trac_auth'] = cookie.value
            req.outcookie['trac_auth']['path'] = cookie_path
            req.outcookie['trac_auth']['expires'] = cookie_lifetime
            req.outcookie['trac_auth_session'] = int(time.time())
            req.outcookie['trac_auth_session']['path'] = cookie_path
            req.outcookie['trac_auth_session']['expires'] = cookie_lifetime
            try:
                if self.env.secure_cookies:
                    req.outcookie['trac_auth']['secure'] = True
                    req.outcookie['trac_auth_session']['secure'] = True
            except AttributeError:
                # Report details about Trac compatibility for the feature.
                self.env.log.debug(
                    """Restricting cookies to HTTPS connections is requested,
                    but is supported only by Trac 0.11.2 or later version.
                    """)
        return name

    # overrides
    def _do_login(self, req):
        if not req.remote_user:
            if req.method == 'GET':
                # Trac before 0.12 has known weak redirect loop protection.
                # Adding redirect fix from Trac 0.12, and especially avert
                # from 'self._redirect_back', when we see a 'GET' here.
                referer = req.get_header('Referer')
                # Steer clear of requests going nowhere or loop to self
                if referer is None or \
                        referer.startswith(str(req.abs_href()) + '/login'):
                    referer = req.abs_href()
                req.redirect(referer)
            self._redirect_back(req)
        res = auth.LoginModule._do_login(self, req)

        cookie_path = self._get_cookie_path(req)
        # Fix for Trac 0.11, that always sets path to `req.href()`.
        req.outcookie['trac_auth']['path'] = cookie_path
        # Inspect current cookie and try auth data distribution for SSO.
        cookie = req.outcookie.get('trac_auth')
        if cookie:
            self._distribute_cookie(req, cookie.value)

        if req.args.get('rememberme', '0') == '1':
            # Check for properties to be set in auth cookie.
            cookie_lifetime = self.cookie_lifetime
            req.outcookie['trac_auth']['expires'] = cookie_lifetime
            
            # This cookie is used to indicate that the user is actually using
            # the "Remember me" feature. This is necessary for 
            # '_get_name_for_cookie()'.
            req.outcookie['trac_auth_session'] = 1
            req.outcookie['trac_auth_session']['path'] = cookie_path
            req.outcookie['trac_auth_session']['expires'] = cookie_lifetime
            try:
                if self.env.secure_cookies:
                    req.outcookie['trac_auth_session']['secure'] = True
            except AttributeError:
                # Report details about Trac compatibility for the feature.
                self.env.log.debug(
                    """Restricting cookies to HTTPS connections is requested,
                    but is supported only by Trac 0.11.2 or later version.
                    """)
        else:
            # In Trac 0.12 the built-in authentication module may have already
            # set cookie's expires attribute, so because the user did not
            # check 'remember me' we need to delete it here to ensure that the
            # cookie will still expire at the end of the session.
            try:
                del req.outcookie['trac_auth']['expires']
            except KeyError:
                pass
            # If there is a left-over session cookie from a previous
            # authentication session, expire it now.
            if 'trac_auth_session' in req.incookie:
                self._expire_session_cookie(req)
        return res

    def _distribute_cookie(self, req, trac_auth):
        # Single Sign On authentication distribution between multiple
        #   Trac environments managed by AccountManager.
        all_envs = get_environments(req.environ)
        local_environ = req.environ.get('SCRIPT_NAME', None)
        self.auth_share_participants = []

        for environ, path in all_envs.iteritems():
            if not environ == local_environ.lstrip('/'):
                # Cache environment for subsequent invocations.
                env = open_environment(path, use_cache=True)
                # Consider only Trac environments with equal, non-default
                #   'auth_cookie_path', which enables cookies to be shared.
                if self._get_cookie_path(req) == self.auth_cookie_path:
                    db = env.get_db_cnx()
                    cursor = db.cursor()
                    # Authentication cookie values must be unique. Ensure,
                    #   there is no other session (or worst: session ID)
                    #   associated to it.
                    cursor.execute("""
                        DELETE FROM auth_cookie
                        WHERE  cookie=%s
                        """, (trac_auth,))
                    cursor.execute("""
                        INSERT INTO auth_cookie
                               (cookie,name,ipnr,time)
                        VALUES (%s,%s,%s,%s)
                        """, (trac_auth, req.remote_user, req.remote_addr,
                              int(time.time())))
                    db.commit()
                    env.log.debug('Auth data received from: ' + local_environ)
                    # Track env paths for easier auth revocation later on.
                    self.auth_share_participants.append(path)
                    self.log.debug('Auth distribution success: ' + environ)
                else:
                    self.log.debug('Auth distribution skipped: ' + environ)

    def _get_cookie_path(self, req):
        """Determine "path" cookie property from setting or request object."""
        return '/'

    # overrides
    def _expire_cookie(self, req):
        """Instruct the user agent to drop the auth_session cookie by setting
        the "expires" property to a date in the past.

        Basically, whenever "trac_auth" cookie gets expired, expire
        "trac_auth_session" too.
        """
        # First of all expire trac_auth_session cookie, if it exists.
        if 'trac_auth_session' in req.incookie:
            self._expire_session_cookie(req)
        # Capture current cookie value.
        cookie = req.incookie.get('trac_auth')
        if cookie:
            trac_auth = cookie.value
        else:
            trac_auth = None
        # Then let auth.LoginModule expire all other cookies.
        auth.LoginModule._expire_cookie(self, req)
        # And finally revoke distributed authentication data too.
        if trac_auth:
            for path in self.auth_share_participants:
                env = open_environment(path, use_cache=True)
                db = env.get_db_cnx()
                cursor = db.cursor()
                cursor.execute("""
                    DELETE FROM auth_cookie
                    WHERE  cookie=%s
                    """, (trac_auth,))
                db.commit()
                env.log.debug('Auth data revoked from: ' + \
                              req.environ.get('SCRIPT_NAME', 'unknown'))

    # Keep this code in a separate methode to be able to expire the session
    # cookie trac_auth_session independently of the trac_auth cookie.
    def _expire_session_cookie(self, req):
        """Instruct the user agent to drop the session cookie.

        This is achieved by setting "expires" property to a date in the past.
        """
        cookie_path = self._get_cookie_path(req)
        req.outcookie['trac_auth_session'] = ''
        req.outcookie['trac_auth_session']['path'] = cookie_path
        req.outcookie['trac_auth_session']['expires'] = -10000
        try:
            if self.env.secure_cookies:
                req.outcookie['trac_auth_session']['secure'] = True
        except AttributeError:
            # Report details about Trac compatibility for the feature.
            self.env.log.debug(
                """Restricting cookies to HTTPS connections is requested,
                but is supported only by Trac 0.11.2 or later version.
                """)

    def _remote_user(self, req):
        """The real authentication using configured providers and stores."""
        user = req.args.get('user')
        self.env.log.debug("LoginModule._remote_user: Authentication attempted for '%s'" % user)
        password = req.args.get('password')
        if not user:
            return None
        acctmgr = AccountManager(self.env)
        acctmod = AccountModule(self.env)
        if acctmod.reset_password_enabled == True:
            reset_store = acctmod.store
        else:
            reset_store = None
        if acctmgr.check_password(user, password) == True:
            if reset_store:
                # Purge any temporary password set for this user before,
                # to avoid DOS by continuously triggered resets from
                # a malicious third party.
                if reset_store.delete_user(user) == True and \
                        'PASSWORD_RESET' not in req.environ:
                    db = self.env.get_db_cnx()
                    cursor = db.cursor()
                    cursor.execute("""
                        DELETE
                        FROM    session_attribute
                        WHERE   sid=%s
                            AND name='force_change_passwd'
                            AND authenticated=1
                        """, (user,))
                    db.commit()
            return user
        # Alternative authentication provided by password reset procedure
        elif reset_store:
            if reset_store.check_password(user, password) == True:
                # Lock, required to prevent another authentication
                # (spawned by `set_password()`) from possibly deleting
                # a 'force_change_passwd' db entry for this user.
                req.environ['PASSWORD_RESET'] = user
                # Change password to temporary password from reset procedure
                acctmgr.set_password(user, password)
                return user
        return None

    def _format_ctxtnav(self, items):
        """Prepare context navigation items for display on login page."""
        return list(separated(items, '|'))

    def enabled(self):
        # Trac built-in authentication must be disabled to use this one.
        return is_enabled(self.env, self.__class__) and \
                not is_enabled(self.env, auth.LoginModule)

    enabled = property(enabled)
