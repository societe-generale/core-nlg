# -*- coding: utf-8 -*-
"""
created on 25/07/2019 14:57
@author: fgiely
"""
import pytest
from CoreNLG.DocumentConstructors import Datas, Document
from CoreNLG.NlgTools import NlgTools

from CoreNLG.tests.fixtures import post_treatment_with_synonyms_fr


class TestSynonyms:

    @pytest.mark.parametrize(
            "input",
            [
                [],
                [""],
                ["test"],
                ["test", "syno", "", None]
            ],
        )
    def test_synonym_before_treatment(self, input):
        nlg = NlgTools()
        nlg_syn = nlg.nlg_syn
        assert nlg_syn(input) == "*1*"

    @pytest.mark.parametrize(
        "input",
        [
            ["Test"],
            ["Test1", "Test2", "Test3"]
        ],
    )
    def test_synonym(self, input):
        text = post_treatment_with_synonyms_fr(*input)
        assert text in input

    @pytest.mark.parametrize(
        "input",
        [
            ["Test"],
            ["Test1", "Test2", "Test3"]
        ],
    )
    def test_synonym_random(self, input):
        datas = Datas({})
        doc = Document(datas, lang="fr")
        section = doc.new_section()
        section.text = section.tools.nlg_syn(input, mode="random")
        section.write()
        assert section.html.xpath('//div')[0].text_content() in input

    @pytest.mark.parametrize(
        "input",
        [
            ["Test"],
            ["Test1", "Test2", "Test3"]
        ],
    )
    def test_synonym_freeze(self, input):
        datas = Datas({})
        doc = Document(datas, lang="fr", freeze=True)
        section = doc.new_section()
        section.text = section.tools.nlg_syn(input)
        section.write()
        assert section.html.xpath('//div')[0].text_content() == input[0]

    @pytest.mark.parametrize(
        "input",
        [
            ["Test"],
            ["Test1", "Test2", "Test3"]
        ],
    )
    def test_nested_synonym_freeze(self, input):
        datas = Datas({})
        doc = Document(datas, lang="fr", freeze=True)
        section = doc.new_section()
        section.text = section.tools.nlg_syn(section.tools.nlg_syn(input), section.tools.nlg_syn(input))
        section.write()
        assert section.html.xpath('//div')[0].text_content() == input[0]

    @pytest.mark.parametrize(
        "input",
        [
            ["Test"],
            ["Test1", "Test2", "Test3"]
        ],
    )
    def test_nested_synonym(self, input):
        datas = Datas({})
        doc = Document(datas, lang="fr")
        section = doc.new_section()
        section.text = section.tools.nlg_syn(section.tools.nlg_syn(input), section.tools.nlg_syn(input))
        section.write()
        assert section.html.xpath('//div')[0].text_content() in input

    @pytest.mark.parametrize(
        "",
        [
            "" for i in range(10)
        ],
    )
    def test_multi_synonym_keyval(self):
        datas = Datas({})
        doc = Document(datas, lang="fr")
        section = doc.new_section()
        syno1 = ("word", "TEST_1")
        syno2 = ("term", "TEST_2")
        section.text = section.tools.nlg_syn(syno1, syno2)
        section.text = section.tools.post_eval("TEST_1", section.tools.nlg_syn(syno2), section.tools.nlg_syn(syno1))
        section.write()
        expected_result = [
            "Word term",
            "Term word"
        ]
        assert section.html.xpath('//div')[0].text_content() in expected_result

    @pytest.mark.parametrize(
        "",
        [
            "" for i in range(30)
        ],
    )
    def test_multi_synonym(self):
        datas = Datas({})
        doc = Document(datas, lang="fr")
        section = doc.new_section()
        synos = ["word", "term", "note"]
        section.text = section.tools.nlg_syn(synos)
        section.text = section.tools.nlg_syn(synos)
        section.text = section.tools.nlg_syn(synos)
        section.write()
        expected_output = [
            "Word term note",
            "Word note term",
            "Note word term",
            "Note term word",
            "Term word note",
            "Term note word"
        ]
        assert section.html.xpath('//div')[0].text_content() in expected_output

    # @pytest.mark.parametrize(
    #     "",
    #     [
    #         "" for i in range(1)
    #     ],
    # )
    # def test_nested_synonym_keyval(self):
    #     datas = Datas({})
    #     doc = Document(datas, lang="fr")
    #     section = doc.new_section()
    #     section.text = section.tools.nlg_syn(section.tools.nlg_syn(("word", "TEST_1"), "term"))
    #     section.text = section.tools.post_eval("TEST_1", "test", "")
    #     section.write()
    #     expected_output = [
    #         "Word test",
    #         "Term"
    #     ]
    #     assert section.html.xpath('//div')[0].text_content() in expected_output

    @pytest.mark.parametrize(
        "input, expected",
        [
            (("test", "TEST_KEYVAL"), "Test post"),
            ("test", "Test")
        ],
    )
    def test_keyval(self, input, expected):
        datas = Datas({})
        doc = Document(datas, lang="fr")
        section = doc.new_section()
        section.text = section.tools.nlg_syn(input)
        section.text = section.tools.post_eval("TEST_KEYVAL", "post", "")
        section.write()
        assert section.html.xpath('//div')[0].text_content() == expected


