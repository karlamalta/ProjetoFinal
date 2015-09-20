# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 Pedro Algarvio <ufs@ufsoft.org>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Pedro Algarvio <ufs@ufsoft.org>

import re

from trac import __version__
from trac.core import Component, implements
from trac.admin import IAdminPanelProvider
from trac.config import Option, ListOption
from trac.notification import NotifyEmail

from acct_mgr.api import IAccountChangeListener, CommonTemplateProvider, \
                         _, dgettext


class AccountChangeListener(Component):

    implements(IAccountChangeListener)

    _notify_actions = ListOption(
        'account-manager', 'notify_actions', [],
        doc="""Comma separated list of actions to notify of.
        Available actions 'new', 'change', 'delete'.""")

    # IAccountChangeListener methods

    def user_created(self, username, password):
        if 'new' in self._notify_actions:
            notifier = AccountChangeNotification(self.env)
            notifier.notify(username, 'New user registration')

    def user_password_changed(self, username, password):
        if 'change' in self._notify_actions:
            notifier = AccountChangeNotification(self.env)
            notifier.notify(username, 'Password reset for user')

    def user_deleted(self, username):
        if 'delete' in self._notify_actions:
            notifier = AccountChangeNotification(self.env)
            notifier.notify(username, 'Deleted User')

    def user_password_reset(self, username, email, password):
        notifier = PasswordResetNotification(self.env)
        if email != notifier.email_map.get(username):
            raise Exception(
                _("The email and username do not match a known account."))
        notifier.notify(username, password)

    def user_email_verification_requested(self, username, token):
        notifier = EmailVerificationNotification(self.env)
        notifier.notify(username, token)


class AccountChangeNotification(NotifyEmail):
    template_name = 'user_changes_email.txt'

    _recipients = Option(
        'account-manager', 'account_changes_notify_addresses', '',
        """List of email addresses that get notified of user changes, ie,
        new user, password change and delete user.""")

    def get_recipients(self, resid):
        recipients = self._recipients.split()
        return (recipients,[])

    def notify(self, username, action):
        self.data.update({
            'account': {
                'username': username,
                'action': action
            },
            'login': {
                'link': self.env.abs_href.login(),
            }
        })

        projname = self.config.get('project', 'name')
        subject = '[%s] %s: %s' % (projname, action, username)

        NotifyEmail.notify(self, username, subject)


class SingleUserNotification(NotifyEmail):
    """Helper class used for account email notifications which should only be
    sent to one persion, not including the rest of the normally CCed users
    """
    _username = None

    def get_recipients(self, resid):
        return ([resid],[])

    def get_smtp_address(self, addr):
        """Overrides `get_smtp_address` in order to prevent CCing users
        other than the user whose password is being reset.
        """
        if addr == self._username:
            return NotifyEmail.get_smtp_address(self, addr)
        else:
            return None

    def notify(self, username, subject):
        # save the username for use in `get_smtp_address`
        self._username = username
        old_public_cc = self.config.getbool('notification', 'use_public_cc')
        # override public cc option so that the user's email is included in the To: field
        self.config.set('notification', 'use_public_cc', 'true')
        try:
            NotifyEmail.notify(self, username, subject)
        # DEVEL: Better use new 'finally' statement here, but
        #   still need to care for Python 2.4 (RHEL5.x) for now
        except:
            pass
        self.config.set('notification', 'use_public_cc', old_public_cc)


class PasswordResetNotification(SingleUserNotification):
    template_name = 'reset_password_email.txt'

    def notify(self, username, password):
        self.data.update({
            'account': {
                'username': username,
                'password': password,
            },
            'login': {
                'link': self.env.abs_href.login(),
            }
        })

        projname = self.config.get('project', 'name')
        subject = '[%s] Trac password reset for user: %s' % (projname, username)

        SingleUserNotification.notify(self, username, subject)


class EmailVerificationNotification(SingleUserNotification):
    template_name = 'verify_email.txt'

    def notify(self, username, token):
        self.data.update({
            'account': {
                'username': username,
                'token': token,
            },
            'verify': {
                'link': self.env.abs_href.verify_email(token=token,verify=1),
            }
        })

        projname = self.config.get('project', 'name')
        subject = '[%s] Trac email verification for user: %s' % (projname, username)

        SingleUserNotification.notify(self, username, subject)


class AccountChangeNotificationAdminPanel(CommonTemplateProvider):

    implements(IAdminPanelProvider)

    # IAdminPageProvider methods

    def get_admin_panels(self, req):
        if req.perm.has_permission('ACCTMGR_CONFIG_ADMIN'):
            yield ('accounts', _("Accounts"), 'notification', _("Notification"))

    def render_admin_panel(self, req, cat, page, path_info):
        if page == 'notification':
            return self._do_config(req)

    def _do_config(self, req):
        if req.method == 'POST':
            self.config.set(
                'account-manager', 'account_changes_notify_addresses',
                ' '.join(req.args.get('notify_addresses').strip('\n').split()))

            self.config.set('account-manager', 'notify_actions',
                ','.join(req.args.getlist('notify_actions'))
                )
            self.config.save()
        notify_addresses = self.config.get(
            'account-manager', 'account_changes_notify_addresses').split()
        notify_actions = self.config.getlist('account-manager',
                                             'notify_actions')
        data = {'_dgettext': dgettext,
                'notify_actions': notify_actions,
                'notify_addresses': notify_addresses
               }
        return 'admin_accountsnotification.html', data
