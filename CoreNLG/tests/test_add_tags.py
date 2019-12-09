# -*- coding: utf-8 -*-
"""
created on 24/07/2019 17:09
@author: fgiely
"""
import pytest

from CoreNLG.NlgTools import NlgTools


class TestAddTags:

    nlg = NlgTools()
    add_tag = nlg.add_tag
    iter_elems = nlg.enum

    @pytest.mark.parametrize(
        "tag, expected",
        [
            (None, "tag None doesn't exist in html"),
            ("b", "<b></b>"),
            ("p", "<p></p>"),
            ("div", "<div></div>"),
            ("DIV", "<div></div>"),
            ("a", "<a></a>"),
            ("u", "<u></u>"),
            ("test", "tag test doesn't exist in html")
        ],
    )
    def test_empty_tag(self, tag, expected):
        assert self.add_tag(tag) == expected

    @pytest.mark.parametrize(
        "tag, text, expected",
        [
            (None, "elem", "tag None doesn't exist in html"),
            ("b", "elem", "<b>elem</b>"),
            ("p", "elem", "<p>elem</p>"),
            ("div", "elem", "<div>elem</div>"),
            ("DIV", "elem", "<div>elem</div>"),
            ("a", "elem", "<a>elem</a>"),
            ("u", "elem", "<u>elem</u>"),
            ("test", "elem", "tag test doesn't exist in html")
        ],
    )
    def test_tag_with_text(self, tag, text, expected):
        assert self.add_tag(tag, text) == expected

    @pytest.mark.parametrize(
        "tag, text, _class, expected",
        [
            (None, "elem", "a_class", "tag None doesn't exist in html"),
            ("b", "elem", "a_class", "<b class=\"a_class\">elem</b>"),
            ("p", "elem", "a_class", "<p class=\"a_class\">elem</p>"),
            ("div", "elem", "a_class", "<div class=\"a_class\">elem</div>"),
            ("DIV", "elem", "a_class", "<div class=\"a_class\">elem</div>"),
            ("a", "elem", "a_class", "<a class=\"a_class\">elem</a>"),
            ("u", "elem", "a_class", "<u class=\"a_class\">elem</u>"),
            ("test", "elem", "a_class", "tag test doesn't exist in html")
        ],
    )
    def test_tag_with_text_and_class(self, tag, text, _class, expected):
        assert self.add_tag(tag, text, _class=_class) == expected

    @pytest.mark.parametrize(
        "tag, text, _class, expected",
        [
            (None, "elem", "a_class", "tag None doesn't exist in html"),
            ("b", "elem", "a_class", "<b other=\"test\" class=\"a_class\">elem</b>"),
            ("p", "elem", "a_class", "<p other=\"test\" class=\"a_class\">elem</p>"),
            ("div", "elem", "a_class", "<div other=\"test\" class=\"a_class\">elem</div>"),
            ("DIV", "elem", "a_class", "<div other=\"test\" class=\"a_class\">elem</div>"),
            ("a", "elem", "a_class", "<a other=\"test\" class=\"a_class\">elem</a>"),
            ("u", "elem", "a_class", "<u other=\"test\" class=\"a_class\">elem</u>"),
            ("test", "elem", "a_class", "tag test doesn't exist in html")
        ],
    )
    def test_tag_with_text_class_and_other(self, tag, text, _class, expected):
        assert self.add_tag(tag, text, _class=_class, other="test") == expected

    def test_tag_encapsuled(self):
        assert self.add_tag("div", self.add_tag("p", self.add_tag("b", ))) == "<div><p><b></b></p></div>"

    def test_iter_tags(self):
        assert self.iter_elems(self.add_tag("b", [t for t in ["test", "iter", "tag"]])) == "<b>test</b> <b>iter</b> <b>tag</b>"

    def test_iter_tags_2(self):
        assert self.iter_elems([self.add_tag("b", t) for t in ["test", "iter", "tag"]]) == "<b>test</b> <b>iter</b> <b>tag</b>"

