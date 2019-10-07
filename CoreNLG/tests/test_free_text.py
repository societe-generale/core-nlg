# -*- coding: utf-8 -*-
"""
created on 24/07/2019 11:35
@author: fgiely
"""

from CoreNLG.helper import NlgTools


class TestFreeText:

    nlg = NlgTools()
    free_text = nlg.free_text

    def test_empty_string(self):
        assert self.free_text("") == ""

    def test_none_string(self):
        assert self.free_text(None) == ""

    def test_empty_list(self):
        assert self.free_text([]) == ""

    def test_list_elem(self):
        assert self.free_text(["elem", "elem"]) == "elem elem"

    def test_list_empty_elem(self):
        assert self.free_text(["elem", "", "elem"]) == "elem  elem"

    def test_mix_list_elem(self):
        assert self.free_text(["elem", "elem"], "elem") == "elem elem elem"

    def test_mix_none_empty_list(self):
        assert (
            self.free_text(["elem", "", None], "elem", None, [""], "", "elem")
            == "elem  elem   elem"
        )
