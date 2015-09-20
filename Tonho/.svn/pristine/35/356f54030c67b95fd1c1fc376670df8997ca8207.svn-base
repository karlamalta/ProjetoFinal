# -*- coding: utf-8 -*-

from trac.ticket.model import Ticket

from ticketref.model import TICKETREF

def create_ticket(env):
    t = Ticket(env)
    t["summary"] = "test"
    t["description"] = "ticket for test"
    t.insert()
    assert t.exists
    return t

def create_tickets(env, num):
    return [create_ticket(env) for _ in range(num)]

def make_simple_ticketref(env):
    t1 = create_ticket(env)
    t2 = create_ticket(env)
    t1[TICKETREF] = u"%s" % t2.id
    assert t1.save_changes()
    t2 = Ticket(env, t2.id)
    assert t2[TICKETREF] == u"%s" % t1.id
    return t1, t2

def make_multi_ticketref(env):
    t1, t2, t3 = create_tickets(env, 3)
    t1[TICKETREF] = u"%s, %s" % (t2.id, t3.id)
    assert t1.save_changes()
    t2, t3 = Ticket(env, t2.id), Ticket(env, t3.id)
    assert t2[TICKETREF] == u"%s" % t1.id
    assert t3[TICKETREF] == u"%s" % t1.id
    return t1, t2, t3
