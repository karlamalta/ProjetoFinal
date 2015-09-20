# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Matthew Good <trac@matt-good.net>
# Copyright (C) 2011 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Matthew Good <trac@matt-good.net>

from binascii import hexlify
from os import urandom

from trac.core import Component, Interface, implements
from trac.config import Option

from acct_mgr.api import AccountManager, _, N_
from acct_mgr.hashlib_compat import md5, sha1
from acct_mgr.md5crypt import md5crypt

try:
    from passlib.apps import custom_app_context as passlib_ctxt
except ImportError:
    # not available
    # Hint: Python2.5 is required too
    passlib_ctxt = None


class IPasswordHashMethod(Interface):
    def generate_hash(user, password):
        pass

    def check_hash(user, password, hash):
        pass


class HtPasswdHashMethod(Component):
    implements(IPasswordHashMethod)

    hash_type = Option('account-manager', 'db_htpasswd_hash_type', 'crypt',
        doc = N_("Default hash type of new/updated passwords"))

    def generate_hash(self, user, password):
        password = password.encode('utf-8')
        return mkhtpasswd(password, self.hash_type)

    def check_hash(self, user, password, hash):
        password = password.encode('utf-8')
        hash2 = htpasswd(password, hash)
        return hash == hash2


class HtDigestHashMethod(Component):
    implements(IPasswordHashMethod)

    realm = Option('account-manager', 'db_htdigest_realm', '',
        doc = N_("Realm to select relevant htdigest db entries"))

    def generate_hash(self, user, password):
        user,password,realm = _encode(user, password, self.realm)
        return ':'.join([realm, htdigest(user, realm, password)])

    def check_hash(self, user, password, hash):
        return hash == self.generate_hash(user, password)


def _encode(*args):
    return [a.encode('utf-8') for a in args]

# check for the availability of the "crypt" module for checking passwords on
# Unix-like platforms
# MD5 is still used when adding/updating passwords with htdigest
try:
    from crypt import crypt
except ImportError:
    crypt = None

def salt(salt_char_count=8):
    s = ''
    v = long(hexlify(urandom(int(salt_char_count/8*6))), 16)
    itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    for i in range(int(salt_char_count)):
        s += itoa64[v & 0x3f]; v >>= 6
    return s

def hash_prefix(hash_type):
    """Map hash type to salt prefix."""
    if hash_type == 'md5':
        return '$apr1$'
    elif hash_type == 'sha':
        return '{SHA}'
    elif hash_type == 'sha256':
        return '$5$'
    elif hash_type == 'sha512':
        return '$6$'
    else:
        # use 'crypt' hash by default anyway
        return ''

def htpasswd(password, hash):
    if hash.startswith('$apr1$'):
        return md5crypt(password, hash[6:].split('$')[0], '$apr1$')
    elif hash.startswith('{SHA}'):
        return '{SHA}' + sha1(password).digest().encode('base64')[:-1]
    elif passlib_ctxt is not None and hash.startswith('$5$') and \
            'sha256_crypt' in passlib_ctxt.policy.schemes():
        return passlib_ctxt.encrypt(password, scheme="sha256_crypt",
                                    rounds=5000, salt=hash[3:].split('$')[0])
    elif passlib_ctxt is not None and hash.startswith('$6$') and \
            'sha512_crypt' in passlib_ctxt.policy.schemes():
        return passlib_ctxt.encrypt(password, scheme="sha512_crypt",
                                    rounds=5000, salt=hash[3:].split('$')[0])
    elif crypt is None:
        # crypt passwords are only supported on Unix-like systems
        raise NotImplementedError(_("""The \"crypt\" module is unavailable
                                    on this platform."""))
    else:
        if hash.startswith('$5$') or hash.startswith('$6$'):
            # Import of passlib failed, now check, if crypt is capable.
            if not crypt(password, hash).startswith(hash):
                # No, so bail out.
                raise NotImplementedError(_(
                    """Neither are \"sha2\" hash algorithms supported by the
                    \"crypt\" module on this platform nor is \"passlib\"
                    available."""))
        return crypt(password, hash)

def mkhtpasswd(password, hash_type=''):
    hash_prefix_ = hash_prefix(hash_type)
    if hash_type.startswith('sha') and len(hash_type) > 3:
        salt_ = salt(16)
    else:
        # Don't waste entropy to older hash types.
        salt_ = salt()
    if hash_prefix_ == '':
        if crypt is None:
            salt_ = '$apr1$' + salt_
    else:
        salt_ = hash_prefix_ + salt_
    return htpasswd(password, salt_)

def htdigest(user, realm, password):
    p = ':'.join([user, realm, password])
    return md5(p).hexdigest()
