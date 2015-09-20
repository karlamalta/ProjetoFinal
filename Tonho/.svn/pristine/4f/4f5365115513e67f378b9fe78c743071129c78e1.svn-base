Notes
=====

`TracTicketReferencePlugin`_ adds simple ticket cross-reference for Trac.

Note: TracTicketReference requires Trac 0.12 or higher.

.. _TracTicketReferencePlugin: http://trac-hacks.org/wiki/TracTicketReferencePlugin

What is it?
-----------

This plugin adds "Relationships" fields to each ticket, enabling you
to express cross-reference between tickets.

Features
--------

* Provide simple cross-reference as Trac custom field (``ticketref``)
* Create new ticket with related ticket's field value
* Picking up the referred ticket in comment

Configuration
=============

To enable the plugin::

    [components]
    ticketref.* = enabled

    [ticket-custom]
    ticketref = textarea
    ticketref.label = Relationships
    ticketref.cols = 68
    ticketref.rows = 1

If you want to show more small field, change as follows::

    [ticket-custom]
    ticketref = text
    ticketref.label = Relationships

i18n/l10n Support
-----------------

This plugin is able to localize field label or message.
You can translate into your language using ``ticketref/locale/messages.pot``.
And then, I'm willing to merge your contribution into the distribution.
So, let me know if you localized ``ticketref/locale/messages.pot``.

See also `Localization (L10N) of Trac`_.

.. _Localization (L10N) of Trac: http://trac.edgewall.org/wiki/TracL10N

Acknowledgment
==============

This plugin was inspired by `MasterTicketsPlugin`_.

.. _MasterTicketsPlugin: http://trac-hacks.org/wiki/MasterTicketsPlugin
