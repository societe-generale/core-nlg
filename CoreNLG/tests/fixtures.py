# -*- coding: utf-8 -*-
"""
created on 24/07/2019 14:01
@author: fgiely
"""

import pytest

from CoreNLG.DocumentConstructors import Document, Datas


class MyDatas(Datas):
    def __init__(self, json_in: dict):
        super(MyDatas, self).__init__(json_in)
        self.test_info = json_in["test_info"]


def create_empty_doc():
    datas = Datas({})
    return Document(datas)


def create_empty_section():
    datas = Datas({})
    document = Document(datas)
    return document, document.new_section()


@pytest.fixture()
def list_elem():
    return ["elem1", "elem2", "elem3"]


@pytest.fixture()
def long_list_elem():
    return ["elem1", "elem2", "elem3", "elem4", "elem5", "elem6"]


@pytest.fixture()
def long_list_with_empty_elem():
    return ["elem1", "elem2", "", "elem4", None, "elem6"]


def post_treatment_with_free_text_fr(text_input):
    datas = Datas({})
    doc = Document(datas, lang="fr")
    section = doc.new_section()
    section.text = section.tools.free_text(*text_input)
    section.write()
    return section.html.xpath('//div')[0].text_content()


def post_treatment_with_synonyms_fr(*text_input):
    datas = Datas({})
    doc = Document(datas, lang="fr")
    section = doc.new_section()
    section.text = section.tools.synonym(*text_input)
    section.write()
    return section.html.xpath('//div')[0].text_content()


def post_treatment_with_numbers_fr(num, **kwargs):
    datas = Datas({})
    doc = Document(datas, lang="fr")
    section = doc.new_section()
    section.text = section.tools.number(num, **kwargs)
    section.write()
    return section.html.xpath('//div')[0].text_content()


def iter_elem_with_post_treatment_fr(text_input, iter_const=None):
    datas = Datas({})
    doc = Document(datas, lang="fr")
    section = doc.new_section()
    section.text = section.tools.enum(text_input, iter_const)
    section.write()
    return section.html.xpath('//div')[0].text_content()

