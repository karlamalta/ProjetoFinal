# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 Matthew Good <trac@matt-good.net>
# Copyright (C) 2011,2012 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

from pkg_resources  import resource_filename

from trac.config  import BoolOption, Configuration, ExtensionOption, \
                         Option, OrderedExtensionsOption
from trac.core  import Component, ExtensionPoint, Interface, TracError, \
                       implements
from trac.perm import IPermissionRequestor
from trac.web.chrome  import ITemplateProvider

# Import i18n methods.  Fallback modules maintain compatibility to Trac 0.11
# by keeping Babel optional here.
try:
    from trac.util.translation  import domain_functions
    add_domain, _, N_, gettext, ngettext, tag_ = \
        domain_functions('acct_mgr', ('add_domain', '_', 'N_', 'gettext',
                                      'ngettext', 'tag_'))
    dgettext = None
except ImportError:
    from genshi.builder  import tag as tag_
    from trac.util.translation  import gettext
    _ = gettext
    N_ = lambda text: text
    def add_domain(a,b,c=None):
        pass
    def dgettext(domain, string, **kwargs):
        return safefmt(string, kwargs)
    def ngettext(singular, plural, num, **kwargs):
        string = num == 1 and singular or plural
        kwargs.setdefault('num', num)
        return safefmt(string, kwargs)
    def safefmt(string, kwargs):
        if kwargs:
            try:
                return string % kwargs
            except KeyError:
                pass
        return string

from acct_mgr.model import delete_user, get_user_attribute, \
                           prime_auth_session, set_user_attribute


class IPasswordStore(Interface):
    """An interface for Components that provide a storage method for users and
    passwords.
    """

    def config_key():
        """'''Deprecated''': New implementations should not use this method.

        The prefered way to configure an `IPasswordStore` implemenation is by
        using its class name in the `password_store` option.

        Returns a string used to identify this implementation in the config.
        This password storage implementation will be used, if the value of
        config property "account-manager.password_format" matches.
        """

    def get_users():
        """Returns an iterable of the known usernames."""

    def has_user(user):
        """Returns whether the user account exists."""

    def set_password(user, password, old_password = None):
        """Sets the password for the user.

        This should create the user account, if it doesn't already exist.
        Returns True, if a new account was created, False if an existing
        account was updated.
        """

    def check_password(user, password):
        """Checks if the password is valid for the user.
    
        Returns True, if the correct user and password are specfied.
        Returns False, if the incorrect password was specified.
        Returns None, if the user doesn't exist in this password store.

        Note: Returing `False` is an active rejection of the login attempt.
        Return None to let the authentication eventually fall through to
        next store in a chain.
        """

    def delete_user(user):
        """Deletes the user account.

        Returns True, if the account existed and was deleted, False otherwise.
        """


class IAccountChangeListener(Interface):
    """An interface for receiving account change events."""

    def user_created(user, password):
        """New user (account) created."""

    def user_password_changed(user, password):
        """Password changed."""

    def user_deleted(user):
        """User and related account information have been deleted."""

    def user_password_reset(user, email, password):
        """User password has been reset.

        Note, that this is no longer final, and the old password could still
        be recovered before first successful login with the new password.
        """

    def user_email_verification_requested(user, token):
        """User verification has been requested."""


class IAccountRegistrationInspector(Interface):
    """An interface for Components, that wish to participate in examining
    requests for account creation.

    The check method is called not only by RegistrationModule but when adding
    new users from the user editor in AccountManagerAdminPanel too.
    """

    def render_registration_fields(req, data):
        """Emit one or multiple additional fields for registration form built.

        Returns a dict containing a 'required' and/or 'optional' tuple of
         * Genshi Fragment or valid XHTML markup for registration form
         * modified or unchanged data object (used to render `register.html`)
        If the return value is just a single tuple, its fragment or markup
        will be inserted into the 'required' section.
        """

    def validate_registration(req):
        """Check registration form input.

        Returns a RegistrationError with error message, or None on success.
        """


class AccountManager(Component):
    """The AccountManager component handles all user account management methods
    provided by the IPasswordStore interface.

    The methods will be handled by underlying password storage implementations
    set in trac.ini with the "account-manager.password_store" option.

    The "account-manager.password_store" may be an ordered list of password
    stores, and if so, then each password store is queried in turn.
    """

    implements(IAccountChangeListener, IPermissionRequestor)

    _password_store = OrderedExtensionsOption(
        'account-manager', 'password_store', IPasswordStore,
        include_missing=False,
        doc = N_("Ordered list of password stores, queried in turn."))
    _password_format = Option('account-manager', 'password_format',
        doc="Legacy option, deprecated since acct_mgr-0.1.2")
    _register_check = OrderedExtensionsOption(
        'account-manager', 'register_check', IAccountRegistrationInspector,
        default="""BasicCheck, EmailCheck, BotTrapCheck, RegExpCheck,
                 UsernamePermCheck""",
        include_missing=False,
        doc="""Ordered list of IAccountRegistrationInspector's to use for
        registration checks.""")
    stores = ExtensionPoint(IPasswordStore)
    change_listeners = ExtensionPoint(IAccountChangeListener)
    allow_delete_account = BoolOption(
        'account-manager', 'allow_delete_account', True,
        doc="Allow users to delete their own account.")
    force_passwd_change = BoolOption(
        'account-manager', 'force_passwd_change', True,
        doc="Force the user to change password when it's reset.")
    persistent_sessions = BoolOption(
        'account-manager', 'persistent_sessions', False,
        doc="""Allow the user to be remembered across sessions without
            needing to re-authenticate. This is, user checks a
            \"Remember Me\" checkbox and, next time he visits the site,
            he'll be remembered.""")
    refresh_passwd = BoolOption(
        'account-manager', 'refresh_passwd', False,
        doc="""Re-set passwords on successful authentication.
            This is most useful to move users to a new password store or
            enforce new store configuration (i.e. changed hash type),
            but should be disabled/unset otherwise.""")
    verify_email = BoolOption(
        'account-manager', 'verify_email', True,
        doc="Verify the email address of Trac users.")
    username_char_blacklist = Option(
        'account-manager', 'username_char_blacklist', ':[]',
        doc="""Always exclude some special characters from usernames.
            This is enforced upon new user registration.""")

    def __init__(self):
        # Bind the 'acct_mgr' catalog to the specified locale directory.
        locale_dir = resource_filename(__name__, 'locale')
        add_domain(self.env.path, locale_dir)

    # Public API

    def get_users(self):
        """Get usernames from all active stores.

        Because we allow concurrent active stores, and some stores even don't
        warrant uniqueness within itself, multiple usernames should be
        expected.
        """
        users = []
        for store in self._password_store:
            users.extend(store.get_users())
        return users

    def has_user(self, user):
        exists = False
        user = self.handle_username_casing(user)
        for store in self._password_store:
            if store.has_user(user):
                exists = True
                break
            continue
        return exists

    def set_password(self, user, password, old_password = None):
        user = self.handle_username_casing(user)
        store = self.find_user_store(user)
        if store and not hasattr(store, 'set_password'):
            raise TracError(_(
                """The authentication backend for user %s does not support
                setting the password.
                """ % user))
        elif not store:
            store = self.get_supporting_store('set_password')
        if store:
            if store.set_password(user, password, old_password):
                self._notify('created', user, password)
            else:
                self._notify('password_changed', user, password)
        else:
            raise TracError(_(
                """None of the IPasswordStore components listed in the
                trac.ini supports setting the password or creating users.
                """))

    def check_password(self, user, password):
        valid = False
        user = self.handle_username_casing(user)
        for store in self._password_store:
            valid = store.check_password(user, password)
            if valid:
                if valid == True and (self.refresh_passwd == True) and \
                        self.get_supporting_store('set_password'):
                    self._maybe_update_hash(user, password)
                break
        return valid

    def delete_user(self, user):
        user = self.handle_username_casing(user)
        # Delete from password store 
        store = self.find_user_store(user)
        del_method = getattr(store, 'delete_user', None)
        if callable(del_method):
            del_method(user)
        # Delete session attributes, session and any custom permissions
        # set for the user.
        delete_user(self.env, user)
        self._notify('deleted', user)

    def supports(self, operation):
        try:
            stores = self.password_store
        except AttributeError:
            return False
        else:
            if self.get_supporting_store(operation):
                return True
            else:
                return False

    def password_store(self):
        try:
            return self._password_store
        except AttributeError:
            # fall back on old "password_format" option
            fmt = self._password_format
            for store in self.stores:
                config_key = getattr(store, 'config_key', None)
                if config_key is None:
                    continue
                if config_key() == fmt:
                    return [store]
            # if the "password_format" is not set re-raise the AttributeError
            raise

    password_store = property(password_store)

    def get_supporting_store(self, operation):
        """Returns the IPasswordStore that implements the specified operation.

        None is returned if no supporting store can be found.
        """
        supports = False
        for store in self.password_store:
            if hasattr(store, operation):
                supports = True
                break
            continue
        store = supports and store or None
        return store

    def get_all_supporting_stores(self, operation):
        """Returns a list of stores that implement the specified operation"""
        stores = []
        for store in self.password_store:
            if hasattr(store, operation):
                stores.append(store)
            continue
        return stores

    def find_user_store(self, user):
        """Locates which store contains the user specified.

        If the user isn't found in any IPasswordStore in the chain, None is
        returned.
        """
        user_stores = []
        for store in self._password_store:
            userlist = store.get_users()
            user_stores.append((store, userlist))
            continue
        user = self.handle_username_casing(user)
        for store in user_stores:
            if user in store[1]:
                return store[0]
            continue
        return None

    def handle_username_casing(self, user):
        """Enforce lowercase usernames if required.

        Comply with Trac's own behavior, when case-insensitive
        user authentication is set to True.
        """
        ignore_auth_case = self.config.getbool('trac', 'ignore_auth_case')
        return ignore_auth_case and user.lower() or user

    def validate_registration(self, req):
        """Run configured registration checks and prime account on success."""
        for inspector in self._register_check:
            inspector.validate_registration(req)

        username = self.handle_username_casing(
            req.args.get('username').strip())
        name = req.args.get('name').strip()
        email = req.args.get('email', '').strip()
        # Create the user in the configured (primary) password store.
        self.set_password(username, req.args.get('password'))
        # Output of a successful account creation request is a made-up
        # authenticated session, that a new user can refer to later on.
        prime_auth_session(self.env, username)
        # Save attributes for the user with reference to that session ID.
        for attribute in ('name', 'email'):
            value = req.args.get(attribute)
            if not value:
                continue
            set_user_attribute(self.env, username, attribute, value)

    def _maybe_update_hash(self, user, password):
        if not get_user_attribute(self.env, 1, user, 'password_refreshed', 1):
            self.log.debug("Refresh password for user: %s" % user)
            store = self.find_user_store(user)
            pwstore = self.get_supporting_store('set_password')
            if pwstore.set_password(user, password) == True:
                # Account re-created according to current settings.
                if store and not (store.delete_user(user) == True):
                    self.log.warn(
                        "Failed to remove old entry for user: %s" % user)
            set_user_attribute(self.env, user, 'password_refreshed', 1)

    def _notify(self, mod, *args):
        mod = '_'.join(['user', mod])
        for listener in self.change_listeners:
            getattr(listener, mod)(*args)

    # IAccountChangeListener methods

    def user_created(self, user, password):
        self.log.info("Created new user: %s" % user)

    def user_password_changed(self, user, password):
        self.log.info("Updated password for user: %s" % user)

    def user_deleted(self, user):
        self.log.info("Deleted user: %s" % user)

    def user_password_reset(self, user, email, password):
        self.log.info("Password reset for user: %s, %s" % (user, email))
        
    def user_email_verification_requested(self, user, token):
        self.log.info("Email verification requested for user: %s" % user)

    # IPermissionRequestor methods

    def get_permission_actions(self):
        action = ['ACCTMGR_CONFIG_ADMIN', 'ACCTMGR_USER_ADMIN', 'EMAIL_VIEW',
                  'USER_VIEW']
        actions = [('ACCTMGR_ADMIN', action), action[0],
                   (action[1], action[2:]), action[3]]
        return actions


class CommonTemplateProvider(Component):
    """Generic template provider."""

    implements(ITemplateProvider)

    abstract = True

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return [('acct_mgr', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        Genshi templates.
        """
        return [resource_filename(__name__, 'templates')]
