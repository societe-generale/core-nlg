# -*- coding: utf-8 -*-
"""
created on 21/02/2019 17:27
@author: fgiely
"""

import lxml
from lxml.html import builder
from lxml import etree
from abc import ABCMeta, abstractmethod

from CoreNLG.NlgTools import NlgTools


class Datas:

    def __init__(self, json_in: dict):
        """
        Can be overridden (cf. Readme.md on CoreNLG GitHub) to handle big file.

        :param json_in: file which contains the main data (which will be the source of the text generation)
        :type json_in: dictionary (possibly returned from json.load(open(".json")) )

        :return: a Datas object, to be used in a Document object
        """

        self.json = json_in


class Document:
    def __new__(cls, datas, text_format="html", title="", css_path="css/styles.css", lang="fr", freeze=False):
        formats = ["html", "plain_text"]
        if text_format == "html":
            return DocumentHtml(datas, lang=lang, freeze=freeze, title=title, css_path=css_path)
        elif text_format == "plain_text":
            return DocumentPlain(datas, lang=lang, freeze=freeze)
        elif text_format == "xml":
            return DocumentXml(datas, lang=lang, freeze=freeze, root="document")
        else:
            raise Exception("unknown text format : {}\ntext_format must be one of {}".format(text_format, formats))


class AbstractDocument(object, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, datas, lang, freeze):
        self._lang = lang
        self._freeze = freeze
        self.datas = datas
        self._sections = []

    @abstractmethod
    def new_section(self):
        pass

    def write(self):
        for section in self._sections:
            self.write_section(section)

    @abstractmethod
    def write_section(self, section):
        pass

    def open_in_browser(self):
        pass

    def get_text_details(self):
        return [section.get_text_details() for section in self._sections]

    def get_all_texts(self):
        return [section.get_all_texts() for section in self._sections]


class DocumentHtml(AbstractDocument):
    def __init__(self, datas, lang, freeze, title, css_path):
        super().__init__(datas, lang, freeze)
        self._html = builder.HTML(
            builder.HEAD(
                builder.META(charset="utf-8"),
                builder.TITLE(title),
                builder.LINK(rel="stylesheet", href=css_path),
            ),
            builder.BODY(builder.DIV(id="text_area")),
        )

    def __str__(self):
        """Printing the HTML document with carriage returns"""
        return lxml.html.tostring(
            self._html, pretty_print=True, encoding="utf-8"
        ).decode("utf-8")

    def __repr__(self):
        return self._html

    @property
    def html(self):
        return self._html

    @property
    def api_html(self):
        """Attribute for the HTML string of the document"""
        return lxml.html.tostring(self._html, encoding="utf-8").decode("utf-8")

    def new_section(self, elem=None, elem_attr=None, **kwargs):
        """Creating a new section with a dictionary of data"""
        section = SectionHtml(
            self.datas, self._lang, self._freeze, elem, elem_attr, **kwargs
        )
        self._sections.append(section)
        return section

    def open_in_browser(self):
        lxml.html.open_in_browser(self._html)

    def write_section(self, section, parent_elem=None, parent_id=None):
        """
        Inserts a HTML container inside the document, by default at the end of the div named 'text_area'.

        :param section: a HTML container built with the 'Section' class
        :type section: cf. Section

        :param parent_elem: a HTML container type which is used to place the section inside it (must be in the doc)
        :type parent_elem: a string with the container name (eg. 'table')

        :param parent_id: the 'id' value of an HTML container in the document
        :type parent_id: a string (eg. 'text_area')

        :return: inserts the section inside the document object
        :rtype: None
        """

        section.write()
        if parent_elem is None:
            if parent_id is None:
                self._html.get_element_by_id("text_area").append(section.html)
            else:
                self._html.get_element_by_id(parent_id).append(section.html)
        else:
            if parent_id is not None:
                self._html.get_element_by_id(parent_id).append(section.html)
            else:
                self._html.find(".//" + parent_elem).append(section.html)


class DocumentXml(AbstractDocument):
    def __init__(self, datas, lang, freeze, root="document"):
        super().__init__(datas, lang, freeze)
        self._xml = etree.Element(root)

    def __str__(self):
        """Printing the HTML document with carriage returns"""
        return etree.tostring(self._xml, encoding="utf-8", xml_declaration=True).decode("utf-8")

    def __repr__(self):
        return self._xml

    @property
    def xml(self):
        return self._xml

    def new_section(self, elem=None, elem_attr=None, **kwargs):
        """Creating a new section with a dictionary of data"""
        section = SectionXml(
            self.datas, self._lang, self._freeze, elem, elem_attr, **kwargs
        )
        self._sections.append(section)
        return section

    def write_section(self, section, parent_elem=None, parent_id=None):
        section.write()
        self._xml.append(section.xml)


class DocumentPlain(AbstractDocument):
    def __init__(self, datas, lang, freeze):
        super().__init__(datas, lang, freeze)
        self._text = ""

    def __repr__(self):
        return self._text

    def write_section(self, section):
        section.write()
        self._text += str(section)

    def new_section(self, **kwargs):
        """Creating a new section with a dictionary of data"""
        section = SectionPlain(
            self.datas, self._lang, self._freeze
        )
        self._sections.append(section)
        return section


class AbstractSection(object, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, datas):
        self.__dict__ = datas.__dict__.copy()
        self._text = list()
        self._nlg = None

    @property
    def text(self):
        return " ".join([elem for elem in self._text if elem is not None])

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self._text += [value]
        else:
            f = lambda l: sum(([x] if type(x) not in [list, tuple] else f(x) for x in l), [])
            self._text += f(value)

    def write(self):
        """Uses NlgTools to write the text"""
        self._nlg.write_text(self.text)
        self._text = list()

    @property
    def tools(self) -> NlgTools:
        return self._nlg

    @property
    def html(self):
        return self._nlg.html

    @property
    def xml(self):
        return self._nlg.xml

    @abstractmethod
    def to_file(self, path):
        pass

    def read_old_attribs(self, elem, elem_attr, default, **kwargs):
        if elem is None:
            if "html_elem" in kwargs:
                elem = kwargs["html_elem"]
            else:
                elem = default
        if elem_attr is None:
            if "html_elem_attr" in kwargs:
                elem_attr = kwargs["html_elem_attr"]
        return elem, elem_attr

    def get_text_details(self):
        pass


class SectionHtml(AbstractSection):
    def __init__(self, datas, lang, freeze, elem="div", elem_attr=None, **kwargs):
        super().__init__(datas)
        elem, elem_attr = self.read_old_attribs(elem, elem_attr, "div", **kwargs)
        self._nlg = NlgTools(lang, freeze, elem, elem_attr)

    def __str__(self):
        return lxml.html.tostring(self._nlg.html, encoding="utf-8").decode("utf-8")

    def to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.html)

    def get_text_details(self):
        return self._nlg.get_text_details(self.text)

    def get_all_texts(self):
        return self._nlg.get_all_texts(self.text)


class SectionXml(AbstractSection):
    def __init__(self, datas, lang, freeze, elem=None, elem_attr=None, **kwargs):
        super().__init__(datas)
        elem, elem_attr = self.read_old_attribs(elem, elem_attr, "child", **kwargs)
        self._nlg = NlgTools(lang, freeze, elem, elem_attr)

    def __str__(self):
        return etree.tostring(self._nlg.xml, encoding="utf-8", xml_declaration=True).decode("utf-8")

    def to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.xml)


class SectionPlain(AbstractSection):
    def __init__(self, datas, lang, freeze):
        super().__init__(datas)
        self._nlg = NlgTools(lang, freeze)

    def __str__(self):
        return self._nlg.text

    def to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.text)


class TextClass:
    def __init__(self, section):
        self.section = section
        self.nlg: NlgTools = self.section.tools
        self.nlg_tags = self.nlg.add_tag
        self.nlg_num = self.nlg.nlg_num
        self.nlg_syn = self.nlg.nlg_syn
        self.nlg_iter = self.nlg.enum
        self.nlg_enum = self.nlg.enum
        self.no_interpret = self.nlg.no_interpret
        self.free_text = self.nlg.free_text
        self.post_eval = self.nlg.post_eval

    def __getattr__(self, name):
        try:
            return getattr(self.section, name)
        except AttributeError:
            raise AttributeError("Child' object has no attribute '%s'" % name)

    def __str__(self):
        return self.section.text

    @property
    def text(self):
        return self.section.text

    @text.setter
    def text(self, value):
        self.section.text = value
