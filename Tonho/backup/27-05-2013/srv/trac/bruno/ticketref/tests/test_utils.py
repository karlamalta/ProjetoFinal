# -*- coding: utf-8 -*-
import pytest

from ticketref import utils

@pytest.mark.parametrize(("comment", "except_ids", "expected"), [
    (None, None, set([])),
    (u"", None, set([])),
    (u"refs. #1", None, set([1])),
    (u"refs. #1ab", None, set([1])),
    (u"refs. a#1b", None, set([])),
    (u"some refer #1, #3, some", None, set([1, 3])),
    (u"some refer #1,#3,#5 # 7 some", None, set([1, 3, 5])),
    (u"ref #1,#3  ref, #5 #7 refs", None, set([1, 3])),
    (u"ref #1,#3  ref #5, #7", None, set([1, 3])),
    (u"refs#1", None, set([])),
    (u"reference#1 #3, #5", None, set([1, 3, 5])),
    (u"adding.\\nrefs #1", None, set([1])),
    (u"adding.\\nrefs #1 #3, #5", None, set([1, 3, 5])),
    (u"adding.\\nsecond\\nrefs #2", None, set([2])),
    (u"except ids\\nrefs #1 #3", [3], set([1])),
    (u"except ids\\nrefs #1 #3 #5", [1, 5], set([3])),
    (u"ref. #21", [23], set([21])),
    (u"ref. #21 #22", [23, 24], set([21, 22])),
    (u"ref. #3 #4", [1], set([3, 4])),
    (u"ref. #3 #4", [1, 3], set([4])),
])
def test_get_refs_in_comment(comment, except_ids, expected):
    assert expected == utils.get_refs_in_comment(comment, except_ids)


@pytest.mark.parametrize(("text", "expected"), [
    ("", set([])),
    ("text only", set([])),
    ("#1", set([1])),
    ("refs #1", set([1])),
    ("refs #1, ", set([1])),
    ("refs #1, #2", set([1, 2])),
    ("refs #1,#2,   #3 ids", set([1, 2, 3])),
])
def test_get_ref_ids_in_comment(text, expected):
    assert expected == utils.get_ref_ids_in_comment(text)


@pytest.mark.parametrize(("refs_text", "expected"), [
    (None, set([])),
    ("", set([])),
    (", ", set([])),
    ("1", set([1])),
    ("1, 3", set([1, 3])),
    ("  1,3,   5", set([1, 3, 5])),
    (",  1,3,", set([1, 3])),
    ("1 3", set([1, 3])),
    ("  1 3    5", set([1, 3, 5])),
    (",  1 3 ", set([1, 3])),
    ("#1 3", set([])),
    ("1 a", set([])),
])
def test_cnv_text2list(refs_text, expected):
    assert expected == utils.cnv_text2list(refs_text)


@pytest.mark.parametrize(("refs", "expected"), [
    (set([]), u''),
    (set([1]), u'1'),
    (set([3, 1]), u'1, 3'),
])
def test_cnv_list2text(refs, expected):
    assert expected == utils.cnv_list2text(refs)


@pytest.mark.parametrize(("orig_text", "extra_refs", "expected"), [
    (u"", set([]), u''),
    (u"1", set([]), u'1'),
    (u"", set([3, 1]), u'1, 3'),
    (u"1, 5", set([3, 1]), u'1, 3, 5'),
    (u"2, 1, 5", set([3, 1, 2]), u'1, 2, 3, 5'),
])
def test_cnv_sorted_refs(orig_text, extra_refs, expected):
    assert expected == utils.cnv_sorted_refs(orig_text, extra_refs)
