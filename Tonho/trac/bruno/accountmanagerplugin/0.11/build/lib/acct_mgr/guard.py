# -*- coding: utf-8 -*-
#
# Copyright (C) 2011,2012 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Steffen Hoffmann <hoff.st@web.de>

from datetime import timedelta

from trac.config import IntOption, Option
from trac.core import Component
from trac.util.datefmt import format_datetime, pretty_timedelta
from trac.util.datefmt import to_datetime, to_timestamp

from acct_mgr.api import AccountManager
from acct_mgr.model import del_user_attribute, get_user_attribute
from acct_mgr.model import set_user_attribute, user_known


class AccountGuard(Component):
    """The AccountGuard component protects against brute-force attacks
    on user passwords.

    It does so by adding logging of failed login attempts,
    account status tracking and administative user account locking.
    Configurable time-locks with exponential lock time prolongation
    allow to balance graceful handling of failed login attempts and
    reasonable protection against attempted brute-force attacks. 
    """

    login_attempt_max_count = IntOption(
        'account-manager', 'login_attempt_max_count', 0,
        doc="""Lock user account after specified number of login attempts.
            Value zero means no limit.""")
    user_lock_time = IntOption(
        'account-manager', 'user_lock_time', 0,
        doc="""Drop user account lock after specified time (seconds).
            Value zero means unlimited lock time.""")
    user_lock_max_time = IntOption(
        'account-manager', 'user_lock_max_time', 86400,
        doc="""Limit user account lock time to specified time (seconds).
            This is relevant only with user_lock_time_progression > 1.""")
    user_lock_time_progression = Option(
        'account-manager', 'user_lock_time_progression', '1',
        doc="""Extend user account lock time incrementally. This is
            based on logarithmic calculation and decimal numbers accepted:
            Value '1' means constant lock time per failed login attempt.
            Value '2' means double locktime after 2nd lock activation,
            four times the initial locktime after 3rd, and so on.""")

    def __init__(self):
        # Adjust related values to promote a sane configuration, because the
        # combination of some default values is not meaningful.
        # DEVEL: Causes more issues than what it resolves - almost disabled.
        cfg = self.env.config
        if self.login_attempt_max_count < 0:
            cfg.set('account-manager', 'login_attempt_max_count', 0)
            options = ['user_lock_time', 'user_lock_max_time',
                       'user_lock_time_progression']
            for option in options:
                cfg.remove('account-manager', option)
        elif self.user_lock_max_time < 1:
            cfg.set('account-manager', 'user_lock_max_time',
                    cfg.defaults().get(
                    'account-manager')['user_lock_max_time'])
        else:
            return
        # Write changes back to file to make them permanent, what causes
        # the environment to reload on next request as well.
        cfg.save()

    def failed_count(self, user, ipnr=None, reset=False):
        """Report number of previously logged failed login attempts.

        Enforce login policy with regards to tracking of login attempts
        and user account lock behavior.
        Default `False` for reset value causes logging of another attempt.
        `None` value for reset just reads failed login attempts count.
        `True` value for reset triggers final log deletion.
        """
        if not user or not user_known(self.env, user):
            return 0
        key = 'failed_logins_count'
        value = get_user_attribute(self.env, user, 1, key)
        count = value and user in value and int(value[user][1].get(key)) or 0
        if reset is None:
            # Report failed attempts count only.
            return count
        if not reset:
            # Trigger the failed attempt logger.
            attempts = self.get_failed_log(user)
            log_length = len(attempts)
            if log_length > self.login_attempt_max_count:
                # Truncate attempts list preserving most recent events.
                del attempts[:(log_length - self.login_attempt_max_count)]
            attempts.append({'ipnr': ipnr,
                             'time': to_timestamp(to_datetime(None))})
            count += 1
            # Update or create attempts counter and list.
            set_user_attribute(self.env, user, 'failed_logins', str(attempts))
            set_user_attribute(self.env, user, key, count)
            self.log.debug(
                "AccountGuard.failed_count(%s) = %s" % (user, count))
        else:
            # Delete existing attempts counter and list.
            del_user_attribute(self.env, user, 1, 'failed_logins')
            del_user_attribute(self.env, user, 1, key)
            # Delete the lock count too.
            self.lock_count(user, 'reset')
        return count

    def get_failed_log(self, user):
        """Returns an iterable of previously logged failed login attempts.

        The iterable contains a list of dicts in the following form:
        {'ipnr': ipnr, 'time': time_stamp} or an empty list.
        The time stamp format depends on Trac support for POSIX seconds
        (before 0.12) or POSIX microseconds in more recent Trac versions.
        """
        if not user:
            return []
        attempts = get_user_attribute(self.env, user, 1, 'failed_logins')
        return attempts and eval(attempts[user][1].get('failed_logins')) or []

    def lock_count(self, user, action='get'):
        """Count, log and report, how often in succession user account
        lock conditions have been met.

        This is the exponent for lock time prolongation calculation too.
        """
        key = 'lock_count'
        if action != 'reset':
            value = get_user_attribute(self.env, user, 1, key)
            count = value and user in value and \
                    int(value[user][1].get(key)) or 0
            if action != 'get':
                # Push and create or update cached count.
                count += 1
                set_user_attribute(self.env, user, key, count)
        else:
            # Reset/delete lock count cache.
            del_user_attribute(self.env, user, 1, key)
            count = 0
        return count

    def lock_time(self, user, next=False):
        """Calculate current time-lock length for user account."""
        base = self.lock_time_progression
        lock_count = self.lock_count(user)
        if not user or not user_known(self.env, user):
            return 0
        else:
            if next:
                # Preview calculation.
                exponent = lock_count
            else:
                exponent = lock_count - 1
        t_lock = self.user_lock_time * base ** exponent
        # Limit maximum lock time.
        if t_lock > self.user_lock_max_time:
            t_lock = self.user_lock_max_time
        self.log.debug("AccountGuard.lock_time(%s) = %s%s"
                       % (user, t_lock, next and ' (preview)' or ''))
        return t_lock

    @property
    def lock_time_progression(self):
        try:
            progression = float(self.env.config.get('account-manager',
                                         'user_lock_time_progression'))
            if progression == int(progression):
                progression = int(progression)
            # Prevent unintended decreasing lock time.
            if progression < 1:
                progression = 1
        except (TypeError, ValueError):
            progression = float(self.env.config.defaults().get(
                          'account-manager')['user_lock_time_progression'])
        return progression

    def pretty_lock_time(self, user, next=False):
        """Convenience method for formatting lock time to string."""
        t_lock = self.lock_time(user, next)
        return (t_lock > 0) and \
            (pretty_timedelta(to_datetime(None) - \
             timedelta(seconds = t_lock))) or None

    def pretty_release_time(self, req, user):
        """Convenience method for formatting lock time to string."""
        ts_release = self.release_time(user)
        if ts_release is None:
            return None
        return format_datetime(to_datetime(
            self.release_time(user)), tzinfo=req.tz)

    def release_time(self, user):
        if self.login_attempt_max_count > 0:
            if self.user_lock_time == 0:
                return 0
            # Logged attempts required for further checking.
            attempts = self.get_failed_log(user)
            if attempts:
                return (attempts[-1]['time'] + self.lock_time(user))

    def user_locked(self, user):
        """Returns whether the user account is currently locked.

        Expect True, if locked, False, if not and None otherwise.
        """
        if self.login_attempt_max_count < 1 or not user or \
                not user_known(self.env, user):
            self.log.debug(
                "AccountGuard.user_locked(%s) = None (%s)"
                % (user, self.login_attempt_max_count < 1 and \
                   'disabled by configuration' or 'anonymous user'))
            return None
        count = self.failed_count(user, reset=None)
        if count < self.login_attempt_max_count:
            self.log.debug(
                "AccountGuard.user_locked(%s) = False (try left)" % user)
            return False
        ts_release = self.release_time(user)
        if ts_release == 0:
            # Account locked permanently.
            self.log.debug(
                "AccountGuard.user_locked(%s) = True (permanently)" % user)
            return True
        # Time-locked or time-lock expired.
        ts_now = to_timestamp(to_datetime(None))
        locked = ts_release - ts_now > 0
        self.log.debug(
            "AccountGuard.user_locked(%s) = %s (%s)"
            % (user, locked, locked and 'time-lock' or 'lock expired'))
        return locked
