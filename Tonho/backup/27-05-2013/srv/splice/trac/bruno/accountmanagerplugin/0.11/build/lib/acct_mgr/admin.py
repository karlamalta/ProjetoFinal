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

import inspect
import re

from genshi.builder     import tag
from genshi.core        import Markup

from trac.core          import Component, TracError, implements
from trac.config        import Option
from trac.perm          import PermissionSystem
from trac.util.datefmt  import format_datetime, to_datetime
from trac.util.presentation import Paginator
from trac.web.chrome    import Chrome, add_link, add_notice, add_stylesheet, \
                               add_warning
from trac.admin         import IAdminPanelProvider

from acct_mgr.api       import AccountManager, CommonTemplateProvider, \
                               _, dgettext, gettext, ngettext, tag_
from acct_mgr.guard     import AccountGuard
from acct_mgr.model     import del_user_attribute, email_verified, \
                               get_user_attribute, last_seen, \
                               set_user_attribute
from acct_mgr.register  import EmailVerificationModule, RegistrationError
from acct_mgr.web_ui    import AccountModule
from acct_mgr.util      import is_enabled, get_pretty_dateinfo

try:
    from trac.util  import as_int
except ImportError:
    def as_int(s, default, min=None, max=None):
        """Convert s to an int and limit it to the given range, or
        return default if unsuccessful (copied verbatim from Trac0.12dev).
        """
        try:
            value = int(s)
        except (TypeError, ValueError):
            return default
        if min is not None and value < min:
            value = min
        if max is not None and value > max:
            value = max
        return value

def fetch_user_data(env, req):
    acctmgr = AccountManager(env)
    guard = AccountGuard(env)
    accounts = {}
    for username in acctmgr.get_users():
        if req.perm.has_permission('ACCTMGR_USER_ADMIN'):
            url = req.href.admin('accounts', 'users', user=username)
        else:
            url = None
        accounts[username] = {'username': username, 'review_url': url}
        if guard.user_locked(username):
            accounts[username]['locked'] = True
            t_lock = guard.lock_time(username)
            if t_lock > 0:
                t_release = guard.pretty_release_time(req, username)
                accounts[username]['release_hint'] = _(
                        "Locked until %(t_release)s",
                        t_release=t_release)
    for acct, status in get_user_attribute(env, username=None,
                                           authenticated=None).iteritems():
        account = accounts.get(acct)
        if account is not None and 1 in status:
            # Only use attributes related to authenticated
            # accounts.
            account['name'] = status[1].get('name')
            account['email'] = status[1].get('email')
            if account['email']:
                account['email'] = Chrome(env).format_author(req,
                                                             account['email'])
    ts_seen = last_seen(env)
    if ts_seen is not None:
        for username, last_visit in ts_seen:
            account = accounts.get(username)
            if account and last_visit:
                account['last_visit'] = to_datetime(last_visit)
    return sorted(accounts.itervalues(), key=lambda acct: acct['username'])

def _getoptions(cls):
    opt_cls = isinstance(cls, Component) and cls.__class__ or cls
    options = [(name, value) for name, value in inspect.getmembers(opt_cls)
               if isinstance(value, Option)]
    index = 0
    for option in options:
        index += 1
        try:
            opt_val = option[1].__get__(cls, cls)
        except AttributeError:
            # Error will be raised again when parsing options list,
            # so don't care here.
            continue
        # Check, if option is a valid component (possibly with own options).
        opt_cls = isinstance(opt_val, Component) and opt_val.__class__ or None
        extents = _getoptions(opt_cls)
        for extent in extents:
            options.insert(index, extent)
            index += 1
    return options

def _setorder(req, stores):
    """Pull the password store ordering out of the req object"""
    for store in stores.get_all_stores():
        stores[store] = int(req.args.get(store.__class__.__name__, 0))
        continue


class StoreOrder(dict):
    """Keeps the order of the Password Stores"""

    instance = 0

    def __init__(self, d={}, stores=[], list=[]):
        self.instance += 1
        self.d = {}
        self.sxref = {}
        for store in stores:
            self.d[store] = 0
            self[0] = store
            self.sxref[store.__class__.__name__] = store
            continue
        for i, s in enumerate(list):
            self.d[s] = i + 1
            self[i + 1] = s

    def __getitem__(self, key):
        """Lookup a store in the list"""
        return self.d[key]

    def __setitem__(self, key, value):
        if isinstance(key, Component):
            order = self.d[key]
            self.d[key] = value
            self.d[order].remove(key)
            self[value] = key
        elif isinstance(key, basestring):
            self.d[self.sxref[key]] = value
        elif isinstance(key, int):
            self.d.setdefault(key, [])
            self.d[key].append(value)
        else:
            raise KeyError(_("Invalid key type (%s) for StoreOrder")
                             % str(type(key)))
        pass

    def get_enabled_stores(self):
        """Return an ordered list of password stores

        All stores that are order 0 are dropped from the list.
        """
        keys = [k for k in self.d.keys() if isinstance(k, int)]
        keys.sort()
        storelist = []
        for k in keys[1:]:
            storelist.extend(self.d[k])
            continue
        return storelist

    def get_enabled_store_names(self):
        """Returns the class names of the enabled password stores"""
        stores = self.get_enabled_stores()
        return [s.__class__.__name__ for s in stores]

    def get_all_stores(self):
        return [k for k in self.d.keys() if isinstance(k, Component)]

    def numstores(self):
        return len(self.get_all_stores())


class AccountManagerAdminPanel(CommonTemplateProvider):

    implements(IAdminPanelProvider)

    ACCTS_PER_PAGE = 5

    def __init__(self):
        self.acctmgr = AccountManager(self.env)
        self.guard = AccountGuard(self.env)

    # IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if req.perm.has_permission('ACCTMGR_CONFIG_ADMIN'):
            yield ('accounts', _("Accounts"), 'config', _("Configuration"))
        if req.perm.has_permission('ACCTMGR_USER_ADMIN'):
            yield ('accounts', _("Accounts"), 'users', _("Users"))

    def render_admin_panel(self, req, cat, page, path_info):
        if page == 'config':
            return self._do_config(req)
        elif page == 'users':
            return self._do_users(req)

    def _do_config(self, req):
        stores = StoreOrder(stores=self.acctmgr.stores,
                            list=self.acctmgr.password_store)
        if req.method == 'POST':
            if req.args.get('restart'):
                del_user_attribute(self.env, attribute='password_refreshed')
                req.redirect(req.href.admin('accounts', 'config',
                                            done='restart'))
            _setorder(req, stores)
            self.config.set('account-manager', 'password_store',
                            ','.join(stores.get_enabled_store_names()))
            for store in stores.get_all_stores():
                for attr, option in _getoptions(store):
                    cls_name = store.__class__.__name__
                    newvalue = req.args.get('%s.%s' % (cls_name, attr))
                    self.log.debug("%s.%s: %s" % (cls_name, attr, newvalue))
                    if newvalue is not None:
                        self.config.set(option.section, option.name, newvalue)
                        self.config.save()
            self.config.set('account-manager', 'force_passwd_change',
                            req.args.get('force_passwd_change', False))
            self.config.set('account-manager', 'persistent_sessions',
                            req.args.get('persistent_sessions', False))
            self.config.set('account-manager', 'verify_email',
                            req.args.get('verify_email', False))
            self.config.set('account-manager', 'refresh_passwd',
                            req.args.get('refresh_passwd', False))
            self.config.save()
        sections = []
        for store in self.acctmgr.stores:
            if store.__class__.__name__ == "ResetPwStore":
                # Exclude special store, that is used strictly internally and
                # inherits configuration from SessionStore anyway.
                continue
            options = []
            for attr, option in _getoptions(store):
                error = None
                opt_val = None
                value = None
                try:
                    opt_val = option.__get__(store, store)
                except AttributeError, e:
                    self.env.log.error(e)
                    error = _("""Error while reading configuration -
                              Hint: Enable/install the required component.""")
                    pass
                if opt_val:
                    value = isinstance(opt_val, Component) and \
                            opt_val.__class__.__name__ or opt_val
                opt_sel = None
                try:
                    interface = option.xtnpt.interface
                    opt_sel = {'options': [], 'selected': None}
                except AttributeError:
                    # No ExtensionOption / Interface undefined
                    pass
                if opt_sel:
                    for impl in option.xtnpt.extensions(self.env):
                        extension = impl.__class__.__name__
                        opt_sel['options'].append(extension)
                        if opt_val and extension == value:
                            opt_sel['selected'] = extension
                    if len(opt_sel['options']) == 0 and error:
                        opt_sel['error'] = error
                    value = opt_sel
                options.append(
                            {'label': attr,
                            'name': '%s.%s' % (store.__class__.__name__, attr),
                            'value': value,
                            'doc': gettext(option.__doc__)
                            })
                continue
            sections.append(
                        {'name': store.__class__.__name__,
                        'classname': store.__class__.__name__,
                        'order': stores[store],
                        'options' : options,
                        })
            continue
        sections = sorted(sections, key=lambda i: i['name'])
        numstores = range(0, stores.numstores() + 1)
        data = {
            '_dgettext': dgettext,
            'sections': sections,
            'numstores': numstores,
            'force_passwd_change': self.acctmgr.force_passwd_change,
            'persistent_sessions': self.acctmgr.persistent_sessions,
            'verify_email': self.acctmgr.verify_email,
            'refresh_passwd': self.acctmgr.refresh_passwd
            }
        result = req.args.get('done')
        if result == 'restart':
            data['result'] = _("Password hash refresh procedure restarted.")
        return 'admin_accountsconfig.html', data

    def _do_users(self, req):
        env = self.env
        perm = PermissionSystem(env)
        acctmgr = self.acctmgr
        acctmod = AccountModule(env)
        guard = self.guard
        listing_enabled = acctmgr.supports('get_users')
        create_enabled = acctmgr.supports('set_password')
        password_change_enabled = acctmgr.supports('set_password')
        password_reset_enabled = acctmod.reset_password_enabled
        delete_enabled = acctmgr.supports('delete_user')
        verify_enabled = acctmgr.verify_email and \
                         EmailVerificationModule(env).email_enabled

        account = dict(email=req.args.get('email', '').strip(),
                       name=req.args.get('name', '').strip(),
                       username=acctmgr.handle_username_casing(
                                    req.args.get('username', '').strip()))
        data = {
            '_dgettext': dgettext,
            'acctmgr': account,
            'email_approved': True,
            'listing_enabled': listing_enabled,
            'create_enabled': create_enabled,
            'delete_enabled': delete_enabled,
            'verify_enabled': verify_enabled,
            'ignore_auth_case': self.config.getbool('trac',
                                                    'ignore_auth_case'),
            'password_change_enabled': password_change_enabled,
            'password_reset_enabled': password_reset_enabled
        }
        if req.method == 'GET':
            if 'user' in req.args.iterkeys():
                return self._do_acct_details(req)
            elif req.args.get('max_per_page'):
                return self._do_db_cleanup(req)

        if req.method == 'POST':
            email_approved = req.args.get('email_approved')
            # Preserve selection during a series of requests.
            data['email_approved'] = email_approved

            if req.args.get('add'):
                # Add new user account.
                if create_enabled:
                    # Check request and prime account on success.
                    try:
                        acctmgr.validate_registration(req)
                        # Account email approval for authoritative action.
                        if verify_enabled and email_approved and \
                                account['email']:
                            set_user_attribute(env, account['username'],
                                'email_verification_sent_to', account['email'])
                        # User editor form clean-up.
                        data['acctmgr'] = {}
                    except RegistrationError, e:

                        # Attempt deferred translation.
                        message = gettext(e.message)
                        # Check for (matching number of) message arguments
                        #   before attempting string substitution.
                        if e.msg_args and \
                                len(e.msg_args) == len(re.findall('%s',
                                                                  message)):
                            message = message % e.msg_args
                        data['editor_error'] = Markup(message)
                else:
                    data['editor_error'] = _(
                        "The password store does not support creating users.")
            elif req.args.get('reset') and req.args.get('sel'):
                # Password reset for one or more accounts.
                if password_reset_enabled:
                    sel = req.args.get('sel')
                    sel = isinstance(sel, list) and sel or [sel]
                    for username, name, email in env.get_known_users():
                        if username in sel:
                            acctmod._reset_password(username, email)
                else:
                    data['deletion_error'] = _(
                        "The password reset procedure is not enabled.")
            elif req.args.get('remove') and req.args.get('sel'):
                # Delete one or more accounts.
                if delete_enabled:
                    sel = req.args.get('sel')
                    sel = isinstance(sel, list) and sel or [sel]
                    for account in sel:
                        acctmgr.delete_user(account)
                else:
                    data['deletion_error'] = _(
                        "The password store does not support deleting users.")
            elif req.args.get('change'):
                # Change attributes and or password of existing user account.
                attributes = {
                    'email': _("Email Address"),
                    'name': _("Pre-/Surname (Nickname)"),
                    'password': _("Password")
                    }
                data['success'] = []
                error = TracError('')
                username = acctmgr.handle_username_casing(
                                   req.args.get('username').strip())
                try:
                    if not username:
                        error.account = {'username' : username}
                        error.message = _("Username cannot be empty.")
                        raise error

                    if not acctmgr.has_user(username):
                        error.account = {'username' : username}
                        error.message = _("Unknown user %(user)s.",
                                          user=username)
                        raise error

                    password = req.args.get('password')
                    if password and (password.strip() != ''):
                        if password_change_enabled:
                            if password != req.args.get('password_confirm'):
                                error.message = _("The passwords must match.")
                                raise error
                            acctmgr.set_password(username, password)
                            data['success'].append(attributes.get('password'))
                        else:
                            data['editor_error'] = _(
                                """The password store does not support
                                changing passwords.
                                """)
                    for attribute in ('name', 'email'):
                        value = req.args.get(attribute, '').strip()
                        if value:
                            set_user_attribute(env, username,
                                               attribute, value)
                            data['success'].append(attributes.get(attribute))
                            # Account email approval for authoritative action.
                            if attribute == 'email' and verify_enabled and \
                                    email_approved:
                                set_user_attribute(env, username,
                                    'email_verification_sent_to', value)
                    # User editor form clean-up on success.
                    data['acctmgr'] = {}
                except TracError, e:
                    data['editor_error'] = e.message
                    data['acctmgr'] = getattr(e, 'account', '')
            elif len([action for action in req.args.iterkeys() \
                      if action in ('cleanup' 'purge' 'unselect')]) > 0:
                return self._do_db_cleanup(req)

        # (Re-)Build current user list.
        if listing_enabled:
            data['accounts'] = fetch_user_data(env, req)
            data['cls'] = 'listing'
            data['cols'] = ['email', 'name']
            # Prevent IRequestFilter in trac.timeline.web_ui.TimelineModule
            #   of Trac 0.13 and later from adding a link to timeline by
            #   adding the function with a different key name here.
            data['pretty_date'] = get_pretty_dateinfo(env, req)
        add_stylesheet(req, 'acct_mgr/acct_mgr.css')
        return 'admin_users.html', data

    def _do_acct_details(self, req):
        username = req.args.get('user')
        if not username:
            # Accessing user account details without username is not useful,
            # so we revert such request immediately. 
            add_warning(req, Markup(tag.span(tag_(
                "Please choose account by username from list to proceed."
                ))))
            req.redirect(req.href.admin('accounts', 'users'))

        acctmgr = self.acctmgr
        guard = self.guard

        if req.args.get('update'):
            req.redirect(req.href.admin('accounts', 'users',
                                        user=username))
        elif req.args.get('delete') or req.args.get('release'):
            # delete failed login attempts, evaluating attempts count
            if guard.failed_count(username, reset=True) > 0:
                add_notice(req, Markup(tag.span(Markup(_(
                    "Failed login attempts for user %(user)s deleted",
                    user=tag.b(username)
                    )))))
        elif req.args.get('list'):
            req.redirect(req.href.admin('accounts', 'users'))

        data = {'_dgettext': dgettext,
                'user': username,
               }
        stores = StoreOrder(stores=acctmgr.stores,
                            list=acctmgr.password_store)
        user_store = acctmgr.find_user_store(username)
        if not user_store is None:
            data['user_store'] = user_store.__class__.__name__
            data['store_order_num'] = stores[user_store]
        data['ignore_auth_case'] = \
            self.config.getbool('trac', 'ignore_auth_case')

        for username_, name, email in self.env.get_known_users():
            if username_ == username:
                data['name'] = name
                if email:
                    data['email'] = email
                break
        ts_seen = last_seen(self.env, username)
        if ts_seen is not None:
            data['last_visit'] = format_datetime(ts_seen[0][1], tzinfo=req.tz)

        attempts = []
        attempts_count = guard.failed_count(username, reset = None)
        if attempts_count > 0:
            for attempt in guard.get_failed_log(username):
                t = format_datetime(to_datetime(
                                         attempt['time']), tzinfo=req.tz)
                attempts.append({'ipnr': attempt['ipnr'], 'time': t})
        data['attempts'] = attempts
        data['attempts_count'] = attempts_count
        data['pretty_lock_time'] = guard.pretty_lock_time(username, next=True)
        data['lock_count'] = guard.lock_count(username)
        if guard.user_locked(username) is True:
            data['user_locked'] = True
            data['release_time'] = guard.pretty_release_time(req, username)

        if is_enabled(self.env, EmailVerificationModule) and \
                acctmgr.verify_email is True:
            data['verification'] = 'enabled'
            data['email_verified'] = email_verified(self.env, username, email)
            self.log.debug('AcctMgr:admin:_do_acct_details for user \"' + \
                username + '\", email \"' + str(email) + '\": ' + \
                str(data['email_verified']))

        add_stylesheet(req, 'acct_mgr/acct_mgr.css')
        data['url'] = req.href.admin('accounts', 'users', user=username)
        return 'account_details.html', data

    def _do_db_cleanup(self, req):
        if req.perm.has_permission('ACCTMGR_ADMIN'):
            env = self.env
            changed = False
            # Get all data from 'session_attributes' db table.
            attr = get_user_attribute(self.env, username=None,
                                      authenticated=None)
            attrs = {}
            sel = req.args.get('sel')
            if req.args.get('purge') and sel is not None:
                sel = isinstance(sel, list) and sel or [sel]
                sel_len = len(sel)
                matched = []
                for acct, states in attr.iteritems():
                    for state in states['id'].keys():
                        for elem, id in states[state]['id'].iteritems():
                            if id in sel:
                                if acct in attrs.keys():
                                    if state in attrs[acct].keys():
                                        attrs[acct][state] \
                                            .append(elem)
                                    else:
                                        attrs[acct][state] = [elem]
                                else:
                                    attrs[acct] = {state: [elem]}
                                matched.append(id)
                                if len(matched) == sel_len:
                                    break
                        if len(matched) == sel_len:
                            break
                    if len(matched) == sel_len:
                        break
                for id in (frozenset(sel) - frozenset(matched)):
                    for acct, states in attr.iteritems():
                        for state, id_ in states['id'].iteritems():
                            if id == id_:
                                # Full account is marked, forget attributes.
                                if acct in attrs.keys():
                                    attrs[acct].update({state: []})
                                else:
                                    attrs[acct] = {state: []}
                                matched.append(id)
                                if len(matched) == sel_len:
                                    break
                        if len(matched) == sel_len:
                            break
                # DEVEL: for Python>2.4 better use defaultdict for counters
                del_count = {'acct': 0, 'attr': 0}
                for account, states in attrs.iteritems():
                    for state, elem in states.iteritems():
                        if len(elem) == 0:
                            del_user_attribute(env, account, state)
                            del_count['acct'] += 1
                        else:
                            for attribute in elem:
                                del_user_attribute(env, account, state,
                                                   attribute)
                                del_count['attr'] += 1
                    changed = True
            elif req.args.get('list'):
                req.redirect(req.href.admin('accounts', 'users'))

            if changed == True:
                # Update the dict after changes.
                attr = get_user_attribute(env, username=None,
                                          authenticated=None)
            data = {'_dgettext': dgettext}
            data.update(self._prepare_attrs(req, attr))

            if req.args.get('purge') and sel is not None:
                accounts = attributes = ''
                n_plural=del_count['acct']
                if n_plural > 0:
                    accounts = tag.li(tag.span(tag(ngettext(
                    "%(count)s account",
                    "%(count)s accounts",
                    n_plural, count=n_plural
                ))))
                n_plural=del_count['attr']
                if n_plural > 0:
                    attributes = tag.li(tag.span(tag(ngettext(
                    "%(count)s account attribute",
                    "%(count)s account attributes",
                    n_plural, count=n_plural
                ))))
                data['result'] = tag(_("Successfully deleted:"),
                                     tag.ul(accounts, attributes))
            add_stylesheet(req, 'acct_mgr/acct_mgr.css')
            return 'db_cleanup.html', data

    def _prepare_attrs(self, req, attr):
        page = int(req.args.get('page', '1'))
        # Paginator can't deal with dict, so convert to list.
        attr_lst = [(k,v) for k,v in attr.iteritems()]
        max_per_page = as_int(req.args.get('max_per_page'), None)
        if max_per_page is None:
            max_per_page = self.ACCTS_PER_PAGE
        attr = Paginator(attr_lst, page - 1, max_per_page)

        pagedata = []
        shown_pages = attr.get_shown_pages(21)
        for shown_page in shown_pages:
            page_href = req.href.admin('accounts', 'users', page=shown_page,
                                       max_per_page=max_per_page)
            pagedata.append([page_href, None, str(shown_page),
                             _("page %(num)s", num=str(shown_page))])

        fields = ['href', 'class', 'string', 'title']
        attr.shown_pages = [dict(zip(fields, p)) for p in pagedata]

        attr.current_page = {'href': None, 'class': 'current',
                             'string': str(attr.page + 1), 'title':None}

        if attr.has_next_page:
            next_href = req.href.admin('accounts', 'users', page=page + 1,
                                       max_per_page=max_per_page)
            add_link(req, 'next', next_href, _('Next Page'))

        if attr.has_previous_page:
            prev_href = req.href.admin('accounts', 'users', page=page - 1,
                                       max_per_page=max_per_page)
            add_link(req, 'prev', prev_href, _('Previous Page'))
        page_href = req.href.admin('accounts', 'cleanup')
        return {'attr': attr, 'page_href': page_href}
