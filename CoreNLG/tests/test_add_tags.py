# -*- coding: utf-8 -*-
"""
created on 24/07/2019 17:09
@author: fgiely
"""
import pytest

from CoreNLG.NlgTools import NlgTools


class TestAddTags:

    nlg = NlgTools(lang="en")
    add_tag = nlg.add_tag
    iter_elems = nlg.enum

    @pytest.mark.parametrize(
        "tag, expected",
        [
            ("b", "<b></b>"),
            ("p", "<p></p>"),
            ("div", "<div></div>"),
            ("DIV", "<div></div>"),
            ("a", "<a></a>"),
            ("u", "<u></u>")
        ],
    )
    def test_empty_tag(self, tag, expected):
        assert self.add_tag(tag) == expected

    @pytest.mark.parametrize(
        "tag, text, expected",
        [
            ("b", "elem", "<b>elem</b>"),
            ("p", "elem", "<p>elem</p>"),
            ("div", "elem", "<div>elem</div>"),
            ("DIV", "elem", "<div>elem</div>"),
            ("a", "elem", "<a>elem</a>"),
            ("u", "elem", "<u>elem</u>")
        ],
    )
    def test_tag_with_text(self, tag, text, expected):
        assert self.add_tag(tag, text) == expected

    @pytest.mark.parametrize(
        "tag, text, _class, expected",
        [
            ("b", "elem", "a_class", "<b class=\"a_class\">elem</b>"),
            ("p", "elem", "a_class", "<p class=\"a_class\">elem</p>"),
            ("div", "elem", "a_class", "<div class=\"a_class\">elem</div>"),
            ("DIV", "elem", "a_class", "<div class=\"a_class\">elem</div>"),
            ("a", "elem", "a_class", "<a class=\"a_class\">elem</a>"),
            ("u", "elem", "a_class", "<u class=\"a_class\">elem</u>")
        ],
    )
    def test_tag_with_text_and_class(self, tag, text, _class, expected):
        assert self.add_tag(tag, text, _class=_class) == expected

    @pytest.mark.parametrize(
        "tag, text, _class, expected",
        [
            ("b", "elem", "a_class", "<b class=\"a_class\" other=\"test\">elem</b>"),
            ("p", "elem", "a_class", "<p class=\"a_class\" other=\"test\">elem</p>"),
            ("div", "elem", "a_class", "<div class=\"a_class\" other=\"test\">elem</div>"),
            ("DIV", "elem", "a_class", "<div class=\"a_class\" other=\"test\">elem</div>"),
            ("a", "elem", "a_class", "<a class=\"a_class\" other=\"test\">elem</a>"),
            ("u", "elem", "a_class", "<u class=\"a_class\" other=\"test\">elem</u>")
        ],
    )
    def test_tag_with_text_class_and_other(self, tag, text, _class, expected):
        assert self.add_tag(tag, text, _class=_class, other="test") == expected

    def test_tag_encapsuled(self):
        assert self.add_tag("div", self.add_tag("p", self.add_tag("b", ))) == "<div><p><b></b></p></div>"

    def test_iter_tags(self):
        assert self.iter_elems(self.add_tag("b", [t for t in ["test", "iter", "tag"]])) == "<b>test</b> , <b>iter</b> and <b>tag</b>"

    def test_iter_tags_2(self):
        assert self.iter_elems([self.add_tag("b", t) for t in ["test", "iter", "tag"]]) == "<b>test</b> , <b>iter</b> and <b>tag</b>"

    @pytest.mark.parametrize(
        "tag, text, style, expected",
        [
            ("b", "elem", "color:blue", "<b style=\"color:blue\">elem</b>")
        ],
    )
    def test_tag_with_styles(self, tag, text, style, expected):
        assert self.add_tag(tag, text, style=style) == expected