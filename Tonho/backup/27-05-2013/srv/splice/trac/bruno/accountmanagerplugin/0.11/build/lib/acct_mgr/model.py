# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Steffen Hoffmann <hoff.st@web.de>

from acct_mgr.hashlib_compat  import md5

_USER_KEYS = {
    'auth_cookie': 'name',
    'permission': 'username',
    }


# Public functions

def email_associated(env, email, db=None):
    """Returns whether an authenticated user account with that email address
    exists.
    """
    db = _get_db(env, db)
    cursor = db.cursor()
    cursor.execute("""
        SELECT value
          FROM session_attribute
         WHERE authenticated=1 AND name='email' AND value=%s
        """, (email,))
    for row in cursor:
        return True
    return False

def email_verified(env, user, email, db=None):
    """Returns whether the account and email has been verified.

    Use with care, as it returns the private token string,
    if verification is pending.
    """
    if not user_known(env, user) or not email:
        # Nothing more to check here.
        return None
    db = _get_db(env, db)
    cursor = db.cursor()
    cursor.execute("""
        SELECT value
          FROM session_attribute
         WHERE sid=%s AND name='email_verification_sent_to'
        """, (user,))
    for row in cursor:
        env.log.debug('AcctMgr:model:email_verified for user \"' + \
            user + '\", email \"' + str(email) + '\": ' + str(row[0]))
        if row[0] != email:
            # verification has been sent to different email address
            return None
    cursor.execute("""
        SELECT value
          FROM session_attribute
         WHERE sid=%s AND name='email_verification_token'
        """, (user,))
    for row in cursor:
        # verification token still unverified
        env.log.debug('AcctMgr:model:email_verified for user \"' + \
            user + '\", email \"' + str(email) + '\": ' + str(row[0]))
        return row[0]
    return True

def user_known(env, user, db=None):
    """Returns whether the user has ever been authenticated before."""
    db = _get_db(env, db)
    cursor = db.cursor()
    cursor.execute("""
        SELECT 1
          FROM session
         WHERE authenticated=1 AND sid=%s
        """, (user,))
    for row in cursor:
        return True
    return False


# Utility functions

def get_user_attribute(env, username=None, authenticated=1, attribute=None,
                       value=None, db=None):
    """Return user attributes."""
    ALL_COLS = ('sid', 'authenticated', 'name', 'value')
    columns = []
    constraints = []
    if username is not None:
        columns.append('sid')
        constraints.append(username)
    if authenticated is not None:
        columns.append('authenticated')
        constraints.append(authenticated)
    if attribute is not None:
        columns.append('name')
        constraints.append(attribute)
    if value is not None:
        columns.append('value')
        constraints.append(value)
    sel_columns = [col for col in ALL_COLS if col not in columns]
    if len(sel_columns) == 0:
        # No variable left, so only COUNTing is as a sensible task here. 
        sel_stmt = 'COUNT(*)'
    else:
        if 'sid' not in sel_columns:
            sel_columns.append('sid')
        sel_stmt = ','.join(sel_columns)
    if len(columns) > 0:
        where_stmt = ''.join(['WHERE ', '=%s AND '.join(columns), '=%s'])
    else:
        where_stmt = ''
    sql = """
        SELECT  %s
          FROM  session_attribute
        %s
        """ % (sel_stmt, where_stmt)
    sql_args = tuple(constraints)

    db = _get_db(env, db)
    cursor = db.cursor()
    cursor.execute(sql, sql_args)
    rows = cursor.fetchall()
    if rows is None:
        return {}
    res = {}
    for row in rows:
        if sel_stmt == 'COUNT(*)':
            return [row[0]]
        res_row = {}
        res_row.update(zip(sel_columns, row))
        # Merge with constraints, that are constants for this SQL query.
        res_row.update(zip(columns, constraints))
        account = res_row.pop('sid')
        authenticated = res_row.pop('authenticated')
        # Create single unique attribute ID.
        m = md5()
        m.update(''.join([account, str(authenticated),
                           res_row.get('name')]).encode('utf-8'))
        row_id = m.hexdigest()
        if account in res:
            if authenticated in res[account]:
                res[account][authenticated].update({
                    res_row['name']: res_row['value']
                })
                res[account][authenticated]['id'].update({
                    res_row['name']: row_id
                })
            else:
                res[account][authenticated] = {
                    res_row['name']: res_row['value'],
                    'id': {res_row['name']: row_id}
                }
                # Create account ID for additional authentication state.
                m = md5()
                m.update(''.join([account,
                                  str(authenticated)]).encode('utf-8'))
                res[account]['id'][authenticated] = m.hexdigest()
        else:
            # Create account ID for authentication state.
            m = md5()
            m.update(''.join([account, str(authenticated)]).encode('utf-8'))
            res[account] = {authenticated: {res_row['name']: res_row['value'],
                                            'id': {res_row['name']: row_id}},
                            'id': {authenticated: m.hexdigest()}}
    return res

def prime_auth_session(env, username, db=None):
    """Prime session for registered users before initial login.

    These days there's no distinct user object in Trac, but users consist
    in terms of anonymous or authenticated sessions and related session
    attributes.  So INSERT new sid, needed as foreign key in some db schemata
    later on, at least for PostgreSQL.
    """
    db = _get_db(env, db)
    cursor = db.cursor()
    cursor.execute("""
        SELECT COUNT(*)
          FROM session
         WHERE sid=%s
        """, (username,))
    exists = cursor.fetchone()
    if not exists[0]:
        cursor.execute("""
            INSERT INTO session
                    (sid,authenticated,last_visit)
            VALUES  (%s,1,0)
            """, (username,))
        db.commit()

def set_user_attribute(env, username, attribute, value, db=None):
    """Set or update a Trac user attribute within an atomic db transaction."""
    db = _get_db(env, db)
    cursor = db.cursor()
    sql = """
        WHERE   sid=%s
            AND authenticated=1
            AND name=%s
        """
    cursor.execute("""
        UPDATE  session_attribute
            SET value=%s
        """ + sql, (value, username, attribute))
    cursor.execute("""
        SELECT  value
          FROM  session_attribute
        """ + sql, (username, attribute))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO session_attribute
                    (sid,authenticated,name,value)
            VALUES  (%s,1,%s,%s)
            """, (username, attribute, value))
    db.commit()

def del_user_attribute(env, username=None, authenticated=1, attribute=None,
                       db=None):
    """Delete one or more Trac user attributes for one or more users."""
    columns = []
    constraints = []
    if username is not None:
        columns.append('sid')
        constraints.append(username)
    if authenticated is not None:
        columns.append('authenticated')
        constraints.append(authenticated)
    if attribute is not None:
        columns.append('name')
        constraints.append(attribute)
    if len(columns) > 0:
        where_stmt = ''.join(['WHERE ', '=%s AND '.join(columns), '=%s'])
    else:
        where_stmt = ''
    sql = """
        DELETE
        FROM    session_attribute
        %s
        """ % where_stmt
    sql_args = tuple(constraints)

    db = _get_db(env, db)
    cursor = db.cursor()
    cursor.execute(sql, sql_args)
    db.commit()

def delete_user(env, user, db=None):
    # Delete session attributes, session and any custom permissions
    # set for the user.
    db = _get_db(env, db)
    cursor = db.cursor()
    for table in ['auth_cookie', 'session_attribute', 'session', 'permission']:
        # Preseed, since variable table and column names aren't allowed
        # as SQL arguments (security measure agains SQL injections).
        sql = """
            DELETE
              FROM %s
             WHERE %s=%%s
            """ % (table, _USER_KEYS.get(table, 'sid'))
        cursor.execute(sql, (user,))
    db.commit()
    # DEVEL: Is this really needed?
    db.close()
    env.log.debug("Purged session data and permissions for user '%s'" % user)

def last_seen(env, user=None, db=None):
    db = _get_db(env, db)
    cursor = db.cursor()
    sql = """
        SELECT sid,last_visit
          FROM session
         WHERE authenticated=1
        """
    if user:
        sql += " AND sid=%s"
        cursor.execute(sql, (user,))
    else:
        cursor.execute(sql)
    # Don't pass over the cursor (outside of scope), only it's content.
    res = []
    for row in cursor:
        res.append(row)
    return not len(res) == 0 and res or None


# Internal functions

def _get_db(env, db=None):
    return db or env.get_db_cnx()
