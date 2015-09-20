# -*- coding: utf-8 -*-

import re

def cnv_text2list(refs_text):
    """ convert text to list
    >>> cnv_text2list(None)
    set([])
    >>> cnv_text2list("")
    set([])
    >>> cnv_text2list("1, 3")
    set([1, 3])
    """
    refs = set([])
    if refs_text:
        refs_seq = refs_text.replace(",", " ").split()
        try:
            refs = set([int(id_) for id_ in refs_seq])
        except ValueError:
            pass
    return refs

def cnv_list2text(refs):
    """ convert list to text
    >>> cnv_list2text(set([]))
    u''
    >>> cnv_list2text(set([3, 1]))
    u'1, 3'
    """
    return u", ".join(str(i) for i in sorted(refs))

def cnv_sorted_refs(orig_text, extra_refs):
    """
    >>> cnv_sorted_refs(u"", set([]))
    u''
    >>> cnv_sorted_refs(u"1", set([]))
    u'1'
    >>> cnv_sorted_refs(u"", set([3, 1]))
    u'1, 3'
    >>> cnv_sorted_refs(u"1, 5", set([3, 1]))
    u'1, 3, 5'
    >>> cnv_sorted_refs(u"2, 1, 5", set([3, 1, 2]))
    u'1, 2, 3, 5'
    """
    refs = cnv_text2list(orig_text)
    refs.update(extra_refs)
    return cnv_list2text(refs)
