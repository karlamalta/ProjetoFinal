# -*- coding: utf-8 -*-
from pkg_resources import resource_filename

from genshi.builder import tag
from trac.core import Component, implements
from trac.web.api import IRequestFilter, ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider, add_script, add_stylesheet
from trac.resource import ResourceNotFound
from trac.ticket.model import Ticket
from trac.util.text import shorten_line
from trac.util.translation import domain_functions

from model import TICKETREF as TREF
from utils import cnv_text2list

_, add_domain = domain_functions("ticketref", ("_", "add_domain"))

TEMPLATE_FILES = [
    "report_view.html", "query_results.html", "ticket.html", "query.html",
]

COPY_TICKET_FIELDS = [
    "type", "priority", "milestone", "component", "version", "keywords",
    "owner", "cc",
]


class TicketRefsTemplate(Component):
    """ Extend template for ticket cross-reference """

    implements(IRequestFilter, ITemplateProvider, ITemplateStreamFilter)

    def __init__(self):
        add_domain(self.env.path, resource_filename(__name__, "locale"))
        self.db = self.env.get_db_cnx()
        self.cursor = self.db.cursor()

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        self.log.debug("TicketRefsTemplate: filter_stream start")
        if not data or (not filename in TEMPLATE_FILES):
            return stream

        # For ticket.html
        if "fields" in data and isinstance(data["fields"], list):
            self._filter_fields(req, data)

        # For query_results.html and query.html
        if "groups" in data and isinstance(data["groups"], list):
            self._filter_groups(req, data)

        # For report_view.html
        if "row_groups" in data and isinstance(data["row_groups"], list):
            self._filter_row_groups(req, data)

        self.log.debug("TicketRefsTemplate: filter_stream end")
        return stream

    def _filter_fields(self, req, data):
        self.log.debug("TicketRefsTemplate: _filter_fields start")
        for field in data["fields"]:
            if field["name"] == TREF:
                field["label"] = _("Related Feature")
                field["type"] = _("select")
                c = self.cursor
                c.execute("SELECT id,name FROM projects_feature")
                rows = c.fetchall()
                field["options"] = ['']
                for row in rows :
                    field["options"].append(str(row[0]) + "-" + row[1])
                
                ticket = data["ticket"]
                if ticket[TREF]:
                    field["rendered"] = self._link_refs(req, ticket[TREF],
                                                        verbose_link=True)
        self.log.debug("TicketRefsTemplate: _filter_fields end")
        
    def _filter_groups(self, req, data):
        self.log.debug("TicketRefsTemplate: _filter_groups start")
        fields_tref = data["fields"].get(TREF)
        if fields_tref:  # column checkbox/select option
            fields_tref["label"] = _("Relationships1")
            if fields_tref["type"] == u"textarea":
                if isinstance(data.get("all_columns"), list):
                    data["all_columns"].append(TREF)

        for header in data["headers"]:  # list view header
            if header["name"] == TREF:
                header["label"] = _("Relationships2")

        for group, tickets in data["groups"]:
            for ticket in tickets:
                if TREF in ticket:
                    if TREF in data["row"]:
                        ticket[TREF] = self._link_textarea(req, ticket[TREF])
                    else:  # expect TREF in data["col"]
                        ticket[TREF] = self._link_refs(req, ticket[TREF])
        self.log.debug("TicketRefsTemplate: _filter_groups end")
    def _filter_row_groups(self, req, data):
        self.log.debug("TicketRefsTemplate: _filter_row_groups start")
        for headers in data["header_groups"]:
            for header in headers:
                if header["col"] == TREF:
                    header["title"] = _("Relationships3")
        for group, rows in data["row_groups"]:
            for row in rows:
                _is_list = isinstance(row["cell_groups"], list)
                if "cell_groups" in row and _is_list:
                    for cells in row["cell_groups"]:
                        for cell in cells:
                            if cell.get("header", {}).get("col") == TREF:
                                cell["value"] = self._link_refs(req,
                                                                cell["value"])
        self.log.debug("TicketRefsTemplate: _filter_row_groups end")
        
    def _link_refs(self, req, refs_text, verbose_link=False):
        items_tag = None
        items, verbose_items = [], []
        elem = verbose_elem = "#%s" % refs_text
        try:
            c = self.cursor
            c.execute("SELECT id,name FROM projects_feature WHERE id ='%s'" % refs_text)
            row = c.fetchone()
            if row:
                title = shorten_line(row[1])
                attr = {
                    "class_": "assigned",
                    "href": "/splice/" + str(row[0]),
                    "title": title,
                }
                elem = tag.a("#%s" % refs_text, **attr)
                verbose_elem = tag.a("#%s %s" % (refs_text, title), **attr)
        except ResourceNotFound:
            pass  # not supposed to happen, just in case
        items.extend([elem, ", "])
        verbose_items.extend([verbose_elem, tag.br()])
        if items:
            items_tag = [tag.span(items[:-1], id="tref_ticketid")]
            if verbose_link:
                vattr = {"id": "tref_summary", "class_": "tref-display-none"}
                items_tag.append(tag.span(verbose_items[:-1], **vattr))
        return tag(items_tag)

    def _link_textarea(self, req, refs_text):
        items = []
        for ref_id in sorted(cnv_text2list(refs_text)):
            elem = u"#%s" % ref_id
            try:
                ticket = Ticket(self.env, ref_id)
                if "TICKET_VIEW" in req.perm(ticket.resource):
                    title = shorten_line(ticket["summary"])
                    elem = u"#%s %s" % (ref_id, title)
            except ResourceNotFound:
                pass  # not supposed to happen, just in case
            items.extend([elem, u", "])
        return u"".join(item for item in items[:-1])


    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        self.log.debug("TicketRefsTemplate: post_process_request, %s, %s" % (
                       req.path_info, template))
        if req.path_info.startswith("/ticket/"):
            add_stylesheet(req, "ticketref/ticket.css")
            add_script(req, "ticketref/ticket.js")
        return template, data, content_type

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        yield ("ticketref", resource_filename(__name__, "htdocs"))

    def get_templates_dirs(self):
        return []
