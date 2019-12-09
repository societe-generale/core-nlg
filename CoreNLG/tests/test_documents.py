# -*- coding: utf-8 -*-
"""
created on 25/07/2019 10:58
@author: fgiely
"""

import pytest

from CoreNLG.DocumentConstructors import Datas, Document, TextClass
from CoreNLG.tests.fixtures import create_empty_doc, create_empty_section, MyDatas


class TestDocument:

    def test_document_empty(self):
        document = create_empty_doc()
        expected = "\n".join([
                        '<html>',
                        '<head>',
                        '<meta charset="utf-8">',
                        '<title></title>',
                        '<link rel="stylesheet" href="css/styles.css">',
                        '</head>',
                        '<body><div id="text_area"></div></body>',
                        '</html>\n',
        ])
        assert str(document) == expected

    def test_document_title(self):
        datas = Datas({})
        document = Document(datas, title="test")
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title>test</title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area"></div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_lang(self):
        datas = Datas({})
        document = Document(datas, lang="en")
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area"></div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_css(self):
        datas = Datas({})
        document = Document(datas, css_path="path/to/css")
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="path/to/css">',
            '</head>',
            '<body><div id="text_area"></div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_add_section(self):
        document, section = create_empty_section()
        document.write_section(section)
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area"><div></div></div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_add_section_id(self):
        document = create_empty_doc()
        section = document.new_section(html_elem_attr={"id": "test_section"})
        document.write_section(section)
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area"><div id="test_section"></div></div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_add_two_sections(self):
        document = create_empty_doc()
        section = document.new_section(html_elem_attr={"id": "test_section"})
        document.write_section(section)
        section_2 = document.new_section()
        document.write_section(section_2)
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area">',
            '<div id="test_section"></div>',
            '<div></div>',
            '</div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_add_section_in_other_section_id(self):
        document = create_empty_doc()
        section = document.new_section(html_elem_attr={"id": "test_section"})
        document.write_section(section)
        section_2 = document.new_section()
        document.write_section(section_2, parent_id="test_section")
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area"><div id="test_section"><div></div></div></div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_add_section_in_other_section_elem(self):
        document = create_empty_doc()
        section = document.new_section(html_elem_attr={"id": "test_section"})
        document.write_section(section)
        section_2 = document.new_section()
        document.write_section(section_2, parent_elem="div")
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area">',
            '<div id="test_section"></div>',
            '<div></div>',
            '</div></body>',
            '</html>\n',
        ])
        assert str(document) == expected

    def test_document_add_section_in_other_section_elem_and_id(self):
        document = create_empty_doc()
        section = document.new_section(html_elem_attr={"id": "test_section"})
        document.write_section(section)
        section_2 = document.new_section()
        document.write_section(section_2, parent_elem="div", parent_id="test_section")
        expected = "\n".join([
            '<html>',
            '<head>',
            '<meta charset="utf-8">',
            '<title></title>',
            '<link rel="stylesheet" href="css/styles.css">',
            '</head>',
            '<body><div id="text_area"><div id="test_section"><div></div></div></div></body>',
            '</html>\n',
        ])
        assert str(document) == expected


class TestSection:

    def test_empty_section(self):
        document, section = create_empty_section()
        assert str(section) == "<div></div>\n"

    @pytest.mark.parametrize(
        "input, expected",
        [
            ("div", "<div></div>\n"),
            ("p", "<p></p>\n"),
            ("span", "<span></span>\n"),
            ("a", "<a></a>\n")
        ],
    )
    def test_empty_section_html_element(self, input, expected):
        document = create_empty_doc()
        section = document.new_section(html_elem=input)
        assert str(section) == expected

    def test_wrong_html_element(self):
        document = create_empty_doc()
        with pytest.raises(AttributeError):
            document.new_section(html_elem="wrong")

    @pytest.mark.parametrize(
        "input, expected",
        [
            ({}, "<div></div>\n"),
            ({"id": "test_id"}, "<div id=\"test_id\"></div>\n"),
            ({"class": "test_class"}, "<div class=\"test_class\"></div>\n"),
            ({"any": "test_any"}, "<div any=\"test_any\"></div>\n"),
            ({"id": "test_id", "class": "test_class", "any": "test_any"},
             "<div class=\"test_class\" id=\"test_id\" any=\"test_any\"></div>\n")
        ],
    )
    def test_empty_section_html_attributes(self, input, expected):
        document = create_empty_doc()
        section = document.new_section(html_elem_attr=input)
        assert str(section) == expected

    def test_get_html_text_write_section(self):
        document, section = create_empty_section()
        section.text = "test_text"
        section.write()
        assert str(section) == "<div>Test_text</div>\n"

    def test_get_html_text(self):
        document, section = create_empty_section()
        section.text = "test_text"
        assert str(section) == "<div></div>\n"

    def test_get_html_text_write_document(self):
        document, section = create_empty_section()
        section.text = "test_text"
        document.write_section(section)
        assert str(section) == "<div>Test_text</div>\n"

    def test_get_text(self):
        document, section = create_empty_section()
        section.text = "test_text"
        assert str(section.text) == "test_text"

    def test_get_text_write_section(self):
        document, section = create_empty_section()
        section.text = "test_text"
        section.write()
        assert str(section.text) == ""

    def test_get_html_write_document(self):
        document, section = create_empty_section()
        section.text = "test_text"
        document.write_section(section)
        assert str(section.text) == ""


class TestTextClass:

    def test_empty_text_class(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        assert str(text_class) == ""

    def test_text_class_text(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = "test"
        assert str(text_class) == "test"

    def test_text_class_text_2(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = "test"
        text_class.text = "test"
        assert str(text_class) == "test test"

    def test_text_class_list(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = ["test", "test"]
        assert str(text_class) == "test test"

    def test_text_class_write_get_section_text(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = "test"
        text_class.text = "test"
        assert str(section.text) == "test test"

    def test_text_class_nlg_tag(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = text_class.nlg_tags("b", "test")
        assert str(text_class) == "<b>test</b>"

    def test_text_class_number(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = text_class.nlg_num(154)
        assert str(text_class) == "154"

    def test_text_class_synonym(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = text_class.nlg_syn(["syno"])
        assert str(text_class) == "*1*"

    def test_text_class_iter_elems(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = text_class.nlg_iter([["iter", "elem"]])
        assert str(text_class) == "iter and elem"

    def test_text_class_no_interpret(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = text_class.no_interpret(" ")
        assert str(text_class) == "#SPACE#"

    def test_text_class_free_text(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = text_class.free_text("test")
        assert str(text_class) == "test"

    def test_text_class_post_eval(self):
        document, section = create_empty_section()
        text_class = TextClass(section)
        text_class.text = text_class.post_eval("TEST", "test", "")
        section.write()
        assert section.html.xpath('//div')[0].text_content() == ""


class TestData:

    def test_data_access_json(self):
        datas = MyDatas({"test_info": "test text"})
        document = Document(datas)
        section = document.new_section()
        text_class = TextClass(section)
        text_class.text = text_class.free_text(text_class.json["test_info"])
        assert str(text_class) == "test text"

    def test_data_access_attribute_with_text_class(self):
        datas = MyDatas({"test_info": "test text"})
        document = Document(datas)
        section = document.new_section()
        text_class = TextClass(section)
        text_class.text = text_class.free_text(text_class.test_info)
        assert str(text_class) == "test text"

    def test_data_access_non_existing_json(self):
        datas = MyDatas({"test_info": "test text"})
        document = Document(datas)
        section = document.new_section()
        text_class = TextClass(section)
        with pytest.raises(KeyError):
            text_class.text = text_class.free_text(text_class.json["test_missing"])

    def test_data_access_non_existing_attribute(self):
        datas = MyDatas({"test_info": "test text"})
        document = Document(datas)
        section = document.new_section()
        text_class = TextClass(section)
        with pytest.raises(AttributeError):
            text_class.text = text_class.free_text(text_class.test_missing)
