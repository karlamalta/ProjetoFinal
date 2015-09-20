# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Steffen Hoffmann <hoff.st@web.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Steffen Hoffmann <hoff.st@web.de>

import sys

from trac.env import Environment


env = Environment(sys.argv[1])

if env:
    db = env.get_db_cnx()
    cursor = db.cursor()
    cursor.execute("""
        SELECT sid, value
          FROM session_attribute
         WHERE authenticated=1
           AND name='failed_logins'
    """)
    attempts = []
    fixed = 0
    for sid, failed_logins in cursor:
        l = []
        replace = False
        for attempt in eval(failed_logins):
            time = attempt['time']
            if isinstance(time, long):
                # Convert microseconds to seconds.
                time = int(time / 1000000)
                fixed += 1
                replace = True
            l.append(dict(ipnr=attempt['ipnr'], time=time))
        if replace:
            attempts.append((str(l), sid))
    cursor.executemany("""
        UPDATE session_attribute
           SET value=%s
         WHERE sid=%s
           AND authenticated=1
           AND name='failed_logins'
    """, attempts)
    db.commit()
    print >>sys.stderr, 'INFO: Fixed %s timestamp(s) in %s dataset(s).' \
                         % (fixed, len(attempts))
else:
    print >>sys.stderr, 'Error: Trac environment %s not found.' % sys.argv[1]
    sys.exit(1)
