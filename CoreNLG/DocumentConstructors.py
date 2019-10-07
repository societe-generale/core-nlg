# -*- coding: utf-8 -*-
"""
created on 21/02/2019 17:27
@author: fgiely
"""

import lxml
import os
from lxml.html import builder

from CoreNLG.helper import NlgTools


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
    def __init__(
            self, datas, title="", log_level="ERROR", css_path="css/styles.css", lang="fr", freeze=False
    ):
        """
        Initializing thanks to a JSON (datas)
        HTML document head and body created
        """
        self.__lang = lang
        self.__freeze = freeze
        self.datas = datas
        self.log_level = log_level
        self.__sections = []
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

    @property
    def api_html(self):
        """Attribute for the HTML string of the document"""
        return lxml.html.tostring(self._html, encoding="utf-8").decode("utf-8")

    def open_in_browser(self):
        """Saving and opening the document in the browser"""
        lxml.html.open_in_browser(self._html)

    def new_section(self, html_elem="div", html_elem_attr=None):
        """Creating a new section with a dictionary of data"""
        section = Section(
            self.datas, self.log_level, html_elem, html_elem_attr, self.__lang, self.__freeze
        )
        self.__sections.append(section)
        return section

    def write(self):
        for section in self.__sections:
            self.write_section(section)

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


class Section:
    def __init__(self, datas, log_level, html_elem, html_elem_attr, lang, freeze):
        """A section contains a dictionary of data, a writer using NlgTools, and a text"""
        self.__dict__ = datas.__dict__.copy()
        self.__nlg = NlgTools(html_elem, html_elem_attr, log_level=log_level, lang=lang, freeze=freeze)
        self.__text = list()

    def __str__(self):
        return lxml.html.tostring(
            self.__nlg.html, pretty_print=True, encoding="utf-8"
        ).decode("utf-8")

    @property
    def html(self):
        """HTML getter"""
        return self.__nlg.html

    @property
    def text(self):
        return " ".join([elem for elem in self.__text if elem is not None])

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self.__text += [value]
        else:
            f = lambda l: sum(([x] if type(x) not in [list, tuple] else f(x) for x in l), [])
            self.__text += f(value)

    def write(self):
        """Uses NlgTools to write the text"""
        self.__nlg.write_text(self.text)
        self.__text = list()

    @property
    def tools(self):
        return self.__nlg


class TextClass:
    def __init__(self, section):
        self.section = section
        self.nlg = self.section.tools
        self.nlg_tags = self.section.tools.add_tag
        self.nlg_num = self.section.tools.number
        self.nlg_syn = self.section.tools.synonym
        self.nlg_iter = self.section.tools.iter_elems
        self.nlg_enum = self.section.tools.enum
        self.no_interpret = self.section.tools.no_interpret
        self.free_text = self.section.tools.free_text
        self.post_eval = self.section.tools.post_eval

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
