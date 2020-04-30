# -*- coding: utf-8 -*-
"""
created on 24/07/2019 14:19
@author: fgiely
"""
import pytest

from CoreNLG.tests.fixtures import post_treatment_with_free_text_fr


class TestPostTreatment:
    @pytest.mark.parametrize(
        "text_input, expected",
        [
            ([["elem1", "."], "elem2"], "Elem1. Elem2"),
            (["elem1.elem2"], "Elem1. Elem2"),
            (["elem1..elem2"], "Elem1. Elem2"),
            (["elem1.", ".", "elem2"], "Elem1. Elem2"),
            (["elem1.", "..", "elem2"], "Elem1... Elem2"),
            (["elem1...elem2"], "Elem1... Elem2"),
            ([["elem", "", None], "elem", None, [""], "", "elem"], "Elem elem elem")
        ],
    )
    def test_handle_dot(self, text_input, expected):
        text = post_treatment_with_free_text_fr(text_input)
        assert text == expected

    @pytest.mark.parametrize(
        "text_input, expected",
        [
            (["elem1       elem2"], "Elem1 elem2"),
            (["elem1,elem2   .   elem3     "], "Elem1, elem2. Elem3")
        ],
    )
    def test_remove_multiple_spaces(self, text_input, expected):
        text = post_treatment_with_free_text_fr(text_input)
        assert text == expected

    @pytest.mark.parametrize(
        "text_input, expected",
        [
            (["jusque à"], "Jusqu'à"),
            (["de le"], "Du"),
            (["le arbre"], "L'arbre"),
            (["le école"], "L'école"),
            (["le île"], "L'île"),
            (["jusque à les"], "Jusqu'aux"),
            (["le Arbre"], "L'Arbre"),
            (["De 15   e"], "De 15 e"),
        ],
    )
    def test_contraction_fr(self, text_input, expected):
        text = post_treatment_with_free_text_fr(text_input)
        assert text == expected

    @pytest.mark.parametrize(
        "text_input, expected",
        [
            (["elem1:elem2.elem3!elem4()elem5"], "Elem1 : elem2. Elem3 ! Elem4 () elem5"),
            (["elem1", ":", "elem2", ".elem3", "!", "elem4(", ")", "elem5", "elem6"],
             "Elem1 : elem2. Elem3 ! Elem4 () elem5 elem6"),
        ],
    )
    def test_add_spaces_fr(self, text_input, expected):
        text = post_treatment_with_free_text_fr(text_input)
        assert text == expected

    @pytest.mark.parametrize(
        "text_input, expected",
        [
            (["test.  .. multiple!ponctuation?is working ."], "Test... Multiple ! Ponctuation ? Is working.")
        ],
    )
    def test_tag_with_styles(self, text_input, expected):
        text = post_treatment_with_free_text_fr(text_input)
        assert text == expected

    @pytest.mark.parametrize(
        "text_input, expected",
        [
            (["test .<p> \n<b>capitalize</b>  "], "Test.  \nCapitalize"),
            (["test .<p>  <b>capitalize</b>  "], "Test.  Capitalize")
        ],
    )
    def test_capitalize_with_tags(self, text_input, expected):
        text = post_treatment_with_free_text_fr(text_input)
        assert text == expected
