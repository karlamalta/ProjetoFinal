# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# Copyright (C) 2010-2012 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

import base64
import re
import time

from genshi.core import Markup
from genshi.builder import tag
from os import urandom

from trac import perm, util
from trac.core import Component, TracError, implements
from trac.config import Option
from trac.env import open_environment
from trac.web import auth, chrome
from trac.web.main import IRequestHandler, IRequestFilter

from acct_mgr.api import AccountManager, CommonTemplateProvider, \
                         IAccountRegistrationInspector, \
                         _, N_, dgettext, gettext, tag_
from acct_mgr.model import email_associated, set_user_attribute
from acct_mgr.util import containsAny, is_enabled


class RegistrationError(TracError):
    """Exception raised when a registration check fails."""

    def __init__(self, message, *args, **kwargs):
        """TracError sub-class with extended i18n support.

        It eases error initialization with messages optionally including
        arguments meant for string substitution after deferred translation.
        """
        title = N_("Registration Error")
        tb = 'show_traceback'
        # Care for the 2nd TracError standard keyword argument only.
        show_traceback = tb in kwargs and kwargs.pop(tb, False)
        super(RegistrationError, self).__init__(message, title, show_traceback)
        self.msg_args = args


class GenericRegistrationInspector(Component):
    """Generic check class, great for creating simple checks quickly."""

    implements(IAccountRegistrationInspector)

    abstract = True

    def render_registration_fields(self, req, data):
        """Emit one or multiple additional fields for registration form built.

        Returns a dict containing a 'required' and/or 'optional' tuple of 
         * Genshi Fragment or valid XHTML markup for registration form
         * modified or unchanged data object (used to render `register.html`)
        If the return value is just a single tuple, its fragment or markup
        will be inserted into the 'required' section.
        """
        template = ''
        return template, data

    def validate_registration(self, req):
        """Check registration form input.

        Returns a RegistrationError with error message, or None on success.
        """
        # Nicer than a plain NotImplementedError.
        raise NotImplementedError, _(
            "No check method 'validate_registration' defined in %(module)s",
            module=self.__class__.__name__)


class BasicCheck(GenericRegistrationInspector):
    """A collection of basic checks.

    This includes checking for
     * emptiness (no user input for username and/or password)
     * some blacklisted username characters
     * upper-cased usernames (reserved for Trac permission actions)
     * some reserved usernames
     * a username duplicate in configured password stores
    """

    def validate_registration(self, req):
        acctmgr = AccountManager(self.env)
        username = acctmgr.handle_username_casing(
            req.args.get('username', '').strip())

        if not username:
            raise RegistrationError(N_("Username cannot be empty."))

        # Always exclude some special characters, i.e. 
        #   ':' can't be used in HtPasswdStore
        #   '[' and ']' can't be used in SvnServePasswordStore
        blacklist = acctmgr.username_char_blacklist
        if containsAny(username, blacklist):
            pretty_blacklist = ''
            for c in blacklist:
                if pretty_blacklist == '':
                    pretty_blacklist = tag(' \'', tag.b(c), '\'')
                else:
                    pretty_blacklist = tag(pretty_blacklist,
                                           ', \'', tag.b(c), '\'')
            raise RegistrationError(N_(
                "The username must not contain any of these characters: %s"),
                tag.b(pretty_blacklist)
            )

        # All upper-cased names are reserved for permission action names.
        if username.isupper():
            raise RegistrationError(N_(
                "A username with only upper-cased characters is not allowed.")
            )
 
        # Prohibit some user names, that are important for Trac and therefor
        # reserved, even if not in the permission store for some reason.
        if username.lower() in ['anonymous', 'authenticated']:
            raise RegistrationError(N_("Username %s is not allowed."),
                                    tag.b(username)
            )

        # NOTE: A user may exist in a password store but not in the permission
        #   store.  I.e. this happens, when the user (from the password store)
        #   never logged in into Trac.  So we have to perform this test here
        #   and cannot just check for the user being in the permission store.
        #   And better obfuscate whether an existing user or group name
        #   was responsible for rejection of this user name.
        for store_user in acctmgr.get_users():
            # Do it carefully by disregarding case.
            if store_user.lower() == username.lower():
                raise RegistrationError(N_(
                    "Another account or group already exists, who's name "
                    "differs from %s only by case or is identical."),
                    tag.b(username)
                )

        # Password consistency checks follow.
        password = req.args.get('password')
        if not password:
            raise RegistrationError(N_("Password cannot be empty."))
        elif password != req.args.get('password_confirm'):
            raise RegistrationError(N_("The passwords must match."))


class BotTrapCheck(GenericRegistrationInspector):
    """A collection of simple bot checks.

    This check is bypassed for requests by an admin user.
    """

    reg_basic_token = Option('account-manager', 'register_basic_token', '',
        doc="A string required as input to pass verification.")

    def render_registration_fields(self, req, data):
        """Add a hidden text input field to the registration form, and
        a visible one with mandatory input as well, if token is configured.
        """
        if self.reg_basic_token:
            # Preserve last input for editing on failure instead of typing
            # everything again.
            old_value = req.args.get('basic_token', '')

            # TRANSLATOR: Hint for visible bot trap registration input field.
            hint = tag.p(Markup(_(
                """Please type [%(token)s] as verification token,
                exactly replicating everything within the braces.""",
                token=tag.b(self.reg_basic_token))), class_='hint')
            insert = tag(
                tag.label(_("Parole:"),
                          tag.input(type='text', name='basic_token', size=20,
                                    class_='textwidget', value=old_value)),
                          hint
                )
        else:
            insert = None
        # TRANSLATOR: Registration form hint for hidden bot trap input field.
        insert = tag(insert,
                     tag.input(type='hidden', name='sentinel',
                               title=_("Better do not fill this field."))
                 )
        return insert, data

    def validate_registration(self, req):
        if req.perm.has_permission('ACCTMGR_USER_ADMIN'):
            return
        # Input must be an exact replication of the required token.
        basic_token = req.args.get('basic_token', '')
        # Unlike the former, the hidden bot-trap input field must stay empty.
        keep_empty = req.args.get('sentinel', '')
        if keep_empty or self.reg_basic_token and \
                self.reg_basic_token != basic_token:
            raise RegistrationError(N_("Are you human? If so, try harder!"))


class EmailCheck(GenericRegistrationInspector):
    """A collection of checks for email addresses.

    This check is bypassed, if account verification is disabled.
    """

    def render_registration_fields(self, req, data):
        """Add an email address text input field to the registration form."""
        # Preserve last input for editing on failure instead of typing
        # everything again.
        old_value = req.args.get('email', '').strip()
        insert = tag.label(_("Email:"),
                           tag.input(type='text', name='email', size=20,
                                     class_='textwidget', value=old_value)
                 )
        # Deferred import required to aviod circular import dependencies.
        from acct_mgr.web_ui import AccountModule
        reset_password = AccountModule(self.env).reset_password_enabled
        verify_account = is_enabled(self.env, EmailVerificationModule) and \
                         AccountManager(self.env).verify_email
        if verify_account:
            # TRANSLATOR: Registration form hints for a mandatory input field.
            hint = tag.p(_("""The email address is required for Trac to send
                           you a verification token."""), class_='hint')
            if reset_password:
                hint = tag(hint, tag.p(_(
                           """Entering your email address will also enable you
                           to reset your password if you ever forget it."""),
                           class_='hint')
                       )
            return tag(insert, hint), data
        elif reset_password:
            # TRANSLATOR: Registration form hint, if email input is optional.
            hint = tag.p(_("""Entering your email address will enable you to
                           reset your password if you ever forget it."""),
                         class_='hint')
            return dict(optional=tag(insert, hint)), data
        else:
            # Always return the email text input itself as optional field.
            return dict(optional=insert), data

    def validate_registration(self, req):
        acctmgr = AccountManager(self.env)
        email = req.args.get('email', '').strip()

        if is_enabled(self.env, EmailVerificationModule) and \
                acctmgr.verify_email:
            if not email:
                raise RegistrationError(N_(
                    "You must specify a valid email address.")
                )
            elif email_associated(self.env, email):
                raise RegistrationError(N_(
                    "The email address specified is already in use. "
                    "Please specify a different one.")
                )


class RegExpCheck(GenericRegistrationInspector):
    """A collection of checks based on regular expressions.

    It depends on EmailCheck being enabled too for using it's input field.
    Likewise email checking is bypassed, if account verification is disabled.
    """

    username_regexp = Option('account-manager', 'username_regexp',
        r'(?i)^[A-Z0-9.\-_]{5,}$',
        doc="A validation regular expression describing new usernames.")
    email_regexp = Option('account-manager', 'email_regexp',
        r'(?i)^[A-Z0-9._%+-]+@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$',
        doc="A validation regular expression describing new account emails.")

    def validate_registration(self, req):
        acctmgr = AccountManager(self.env)

        username = acctmgr.handle_username_casing(
            req.args.get('username', '').strip())
        if self.username_regexp != "" and \
                not re.match(self.username_regexp.strip(), username):
            raise RegistrationError(N_(
                "Username %s doesn't match local naming policy."),
                tag.b(username)
            )

        email = req.args.get('email', '').strip()
        if acctmgr.verify_email and is_enabled(self.env, EmailCheck) and \
                is_enabled(self.env, EmailVerificationModule):
            if self.email_regexp.strip() != "" and \
                    not re.match(self.email_regexp.strip(), email):
                raise RegistrationError(N_(
                    "The email address specified appears to be invalid. "
                    "Please specify a valid email address.")
                )


class UsernamePermCheck(GenericRegistrationInspector):
    """Check for usernames referenced in the permission system.

    This check is bypassed for requests by an admin user.
    """

    def validate_registration(self, req):
        if req.perm.has_permission('ACCTMGR_USER_ADMIN'):
            return
        username = AccountManager(self.env).handle_username_casing(
            req.args.get('username', '').strip())

        # NOTE: We can't use 'get_user_permissions(username)' here
        #   as this always returns a list - even if the user doesn't exist.
        #   In this case the permissions of "anonymous" are returned.
        #
        #   Also note that we can't simply compare the result of
        #   'get_user_permissions(username)' to some known set of permission,
        #   i.e. "get_user_permissions('authenticated') as this is always
        #   false when 'username' is the name of an existing permission group.
        #
        #   And again obfuscate whether an existing user or group name
        #   was responsible for rejection of this username.
        for (perm_user, perm_action) in \
                perm.PermissionSystem(self.env).get_all_permissions():
            if perm_user.lower() == username.lower():
                raise RegistrationError(N_(
                    "Another account or group already exists, who's name "
                    "differs from %s only by case or is identical."),
                    tag.b(username)
                )


class RegistrationModule(CommonTemplateProvider):
    """Provides users the ability to register a new account.

    Requires configuration of the AccountManager module in trac.ini.
    """

    implements(chrome.INavigationContributor, IRequestHandler)

    def __init__(self):
        self.acctmgr = AccountManager(self.env)
        self._enable_check(log=True)

    def _enable_check(self, log=False):
        env = self.env
        writable = self.acctmgr.supports('set_password')
        ignore_case = auth.LoginModule(env).ignore_case
        if log:
            if not writable:
                self.log.warn('RegistrationModule is disabled because the '
                              'password store does not support writing.')
            if ignore_case:
                self.log.debug('RegistrationModule will allow lowercase '
                               'usernames only and convert them forcefully '
                               'as required, while \'ignore_auth_case\' is '
                               'enabled in [trac] section of your trac.ini.')
        return is_enabled(env, self.__class__) and writable

    enabled = property(_enable_check)

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'register'

    def get_navigation_items(self, req):
        if not self.enabled:
            return
        if req.authname == 'anonymous':
            yield 'metanav', 'register', tag.a(_("Register"),
                                               href=req.href.register())

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == '/register' and self._enable_check(log=True)

    def process_request(self, req):
        acctmgr = self.acctmgr
        if req.authname != 'anonymous':
            req.redirect(req.href.prefs('account'))
        action = req.args.get('action')
        name = req.args.get('name', '').strip()
        username = acctmgr.handle_username_casing(req.args.get('username',
                                                               '').strip())
        data = {
                '_dgettext': dgettext,
                  'acctmgr': dict(name=name, username=username),
         'ignore_auth_case': self.config.getbool('trac', 'ignore_auth_case')
        }
        verify_enabled = is_enabled(self.env, EmailVerificationModule) and \
                         acctmgr.verify_email
        data['verify_account_enabled'] = verify_enabled
        if req.method == 'POST' and action == 'create':
            try:
                # Check request and prime account on success.
                acctmgr.validate_registration(req)
            except RegistrationError, e:
                # Attempt deferred translation.
                message = gettext(e.message)
                # Check for (matching number of) message arguments before
                #   attempting string substitution.
                if e.msg_args and \
                        len(e.msg_args) == len(re.findall('%s', message)):
                    message = message % e.msg_args
                chrome.add_warning(req, Markup(message))
            else:
                if verify_enabled:
                    chrome.add_notice(req, Markup(tag.span(Markup(_(
                        """Your username has been successfully registered but
                        your account still requires activation. Please login
                        as user %(user)s, and follow the instructions.""",
                        user=tag.b(username)))))
                    )
                    req.redirect(req.href.login())
                chrome.add_notice(req, Markup(tag.span(Markup(_(
                     """Registration has been finished successfully.
                     You may log in as user %(user)s now.""",
                     user=tag.b(username)))))
                )
                req.redirect(req.href.login())
        # Collect additional fields from IAccountRegistrationInspector's.
        fragments = dict(required=[], optional=[])
        for inspector in acctmgr._register_check:
            try:
                fragment, f_data = inspector.render_registration_fields(req,
                                                                        data)
            except TypeError, e:
                # Add some robustness by logging the most likely errors.
                self.env.log.warn("%s.render_registration_fields failed: %s"
                                  % (inspector.__class__.__name__, e))
                fragment = None
            if fragment:
                try:
                    # Python<2.5: Can't have 'except' and 'finally' in same
                    #   'try' statement together.
                    try:
                        if 'optional' in fragment.keys():
                            fragments['optional'].append(fragment['optional'])
                    except AttributeError:
                        # No dict, just append Genshi Fragment or str/unicode.
                        fragments['required'].append(fragment)
                    else:
                        fragments['required'].append(fragment.get('required',
                                                                  ''))
                finally:
                    data.update(f_data)
        data['required_fields'] = fragments['required']
        data['optional_fields'] = fragments['optional']
        return 'register.html', data, None


class EmailVerificationModule(CommonTemplateProvider):
    """Performs email verification on every new or changed address.

    A working email sender for Trac (!TracNotification or !TracAnnouncer)
    is strictly required to enable this module's functionality.

    Anonymous users should register and perms should be tweaked, so that
    anonymous users can't edit wiki pages and change or create tickets.
    So this email verification code won't be used on them. 
    """

    implements(IRequestFilter, IRequestHandler)

    def __init__(self, *args, **kwargs):
        self.email_enabled = True
        if self.config.getbool('announcer', 'email_enabled') != True and \
                self.config.getbool('notification', 'smtp_enabled') != True:
            self.email_enabled = False
            if is_enabled(self.env, self.__class__) == True:
                self.env.log.warn(
                    ' '.join([self.__class__.__name__, 
                              "can't work because of missing email setup."])
                )

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        if not req.session.authenticated:
            # Permissions for anonymous users remain unchanged.
            return handler
        elif req.path_info == '/prefs' and req.method == 'POST' and \
                not 'restore' in req.args:
            try:
                EmailCheck(self.env).validate_registration(req)
                # Check passed without error: New email address seems good.
            except RegistrationError, e:
                # Attempt to change email to an empty or invalid
                # address detected, resetting to previously stored value.
                chrome.add_warning(
                    req, Markup(gettext(e.message)))
                req.redirect(req.href.prefs(None))
        if AccountManager(self.env).verify_email and handler is not self and \
                'email_verification_token' in req.session and \
                not req.perm.has_permission('ACCTMGR_ADMIN'):
            # TRANSLATOR: Your permissions have been limited until you ...
            link = tag.a(_("verify your email address"),
                         href=req.href.verify_email()
                   )
            # TRANSLATOR: ... verify your email address
            chrome.add_warning(req, Markup(tag.span(Markup(_(
                "Your permissions have been limited until you %(link)s.",
                link=link))))
            )
            req.perm = perm.PermissionCache(self.env, 'anonymous')
        return handler

    def post_process_request(self, req, template, data, content_type):
        if not req.session.authenticated:
            # Don't start the email verification procedure on anonymous users.
            return template, data, content_type

        email = req.session.get('email')
        # Only send verification if the user entered an email address.
        acctmgr = AccountManager(self.env)
        if acctmgr.verify_email and self.email_enabled is True and email and \
                email != req.session.get('email_verification_sent_to') and \
                not req.perm.has_permission('ACCTMGR_ADMIN'):
            req.session['email_verification_token'] = self._gen_token()
            req.session['email_verification_sent_to'] = email
            acctmgr._notify(
                'email_verification_requested', 
                req.authname, 
                req.session['email_verification_token']
            )
            # TRANSLATOR: An email has been sent to <%(email)s>
            # with a token to ... (the link label for following message)
            link = tag.a(_("verify your new email address"),
                         href=req.href.verify_email()
                   )
            # TRANSLATOR: ... verify your new email address
            chrome.add_notice(req, Markup(tag.span(Markup(_(
                """An email has been sent to <%(email)s> with a token to
                %(link)s.""", email=email, link=link))))
            )
        return template, data, content_type

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info == '/verify_email'

    def process_request(self, req):
        if not req.session.authenticated:
            chrome.add_warning(req, Markup(tag.span(tag_(
                "Please log in to finish email verification procedure.")))
            )
            req.redirect(req.href.login())
        if 'email_verification_token' not in req.session:
            chrome.add_notice(req, _("Your email is already verified."))
        elif req.method == 'POST' and 'resend' in req.args:
            AccountManager(self.env)._notify(
                'email_verification_requested', 
                req.authname, 
                req.session['email_verification_token']
            )
            chrome.add_notice(req,
                    _("A notification email has been resent to <%s>."),
                    req.session.get('email')
            )
        elif 'verify' in req.args:
            # allow via POST or GET (the latter for email links)
            if req.args['token'] == req.session['email_verification_token']:
                del req.session['email_verification_token']
                chrome.add_notice(
                    req, _("Thank you for verifying your email address.")
                )
                req.redirect(req.href.prefs())
            else:
                chrome.add_warning(req, _("Invalid verification token"))
        data = {'_dgettext': dgettext}
        if 'token' in req.args:
            data['token'] = req.args['token']
        if 'email_verification_token' not in req.session:
            data['button_state'] = { 'disabled': 'disabled' }
        return 'verify_email.html', data, None

    def _gen_token(self):
        return base64.urlsafe_b64encode(urandom(6))
