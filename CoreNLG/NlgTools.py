# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:03
@author: fgiely
"""
import os

from lxml import html
from lxml.html import builder

from CoreNLG.FreeText import FreeText
from CoreNLG.Intensity import Intensity
from CoreNLG.IterElems import IterElems
from CoreNLG.KeyVals import KeyVals
from CoreNLG.Synonym import Synonym
from CoreNLG.decorators import beautifier
from CoreNLG.resources.contraction import contraction

from CoreNLG.AddTag import AddTag
from CoreNLG.Logger import Logger
from CoreNLG.NoInterpret import NoInterpret
from CoreNLG.Number import Number
from CoreNLG.tools import read_json_resource, get_resource_lang, read_default_words, handle_string_to_html


class NlgTools:
    def __init__(
            self,
            html_elem="div",
            html_elem_attr=None,
            log_level="ERROR",
            lang="fr",
            freeze=False,
    ):
        self._html = None
        self.__html_elem_wrap(html_elem, html_elem_attr)
        self._lang = lang
        self._is_beautiful = False

        self._log_level = log_level
        log = Logger(os.path.join(os.getcwd(), "logs"), self._log_level)
        self.logger = log.logger

        self._ponct = None
        self._default_words = None
        self._contract = None
        self.__get_resources()

        self.add_tag = AddTag().add_tag

        self.no_interpret = NoInterpret(add_tag=self.add_tag).no_interpret

        self.nlg_num = Number(
            no_interpret=self.no_interpret,
            sep=read_default_words(self._default_words, "numbers", "sep", default="."),
            mile_sep=read_default_words(self._default_words, "numbers", "mile_sep", default=" "),
        ).nlg_num

        self.enum = IterElems(
            sep=read_default_words(self._default_words, "iter_elems", "sep", default=","),
            last_sep=read_default_words(self._default_words, "iter_elems", "last_sep", default="and"),
        ).enum

        self.__keyvals = KeyVals()
        self.post_eval = self.__keyvals.post_evals

        self.__synonym = Synonym(freeze, self.__keyvals)
        self.nlg_syn = self.__synonym.synonym

        self.free_text = FreeText().free_text

        self.intensity = Intensity().intensity

    @property
    def html(self):
        """
        Ca
        :return:
        """
        self.__beautifier()
        return self._html

    @property
    def html_str(self):
        self.__beautifier()
        return html.tostring(
            self._html, pretty_print=True, encoding="utf-8"
        ).decode("utf-8")

    def write_text(self, *args, no_space=False):
        """Creates a list of string"""
        self._is_beautiful = False
        text = list()
        for arg in args:

            arg = self.__synonym.handle_patterns(arg)
            self.__synonym.update_position(arg)

            text.append(arg)
            if not no_space:
                text.append(" ")

        self.__synonym.smart_syno_lvl = 0
        self.__synonym.synos_by_pattern = {}
        span = handle_string_to_html(
            builder.SPAN, "".join(text), builder.CLASS("to_delete")
        )
        self._html.append(span)
        return span

    def __get_resources(self):
        resource_path = os.path.join(os.path.dirname(__file__), "resources")
        self._ponct = read_json_resource(os.path.join(resource_path, "ponctuation.json"),
                                         self._lang,
                                         self.logger)

        self._default_words = read_json_resource(os.path.join(resource_path, "default_words.json"),
                                                 self._lang,
                                                 self.logger)

        self._contract = get_resource_lang(contraction, self._lang, self.logger)

    def __str__(self):
        self.__beautifier()
        return html.tostring(
            self._html, pretty_print=True, encoding="utf-8"
        ).decode("utf-8")

    def __beautifier(self):
        """

        :return:
        """
        if not self._is_beautiful:
            for span in self._html.xpath("//span[@class='to_delete']"):
                span.drop_tag()
            text = html.tostring(self._html, encoding="utf-8").decode("utf-8")
            self._html = html.fromstring(
                beautifier(text, self._ponct, self._contract)
            )
            self._is_beautiful = True
        return self._html

    def __html_elem_wrap(self, html_elem, html_elem_attr):
        """
        Creates a HTML container

        :param html_elem: name of the HTML element (container) to be created
        :type html_elem: string (eg. 'div')

        :param html_elem_attr: indicates the attributes and their values, in the form {'class': 'a', ...}
        :type html_elem_attr: dictionary (eg. { 'class': 'c', 'is': 'present' })

        :return: an HTML element if a class is in the dictionary, a HTML builder if no class is in the dictionary
        :rtype: if html_elem_attr['class'] exists: lxml.html.htmlElement; otherwise: lxml.html.builder
        """
        tag = getattr(builder, html_elem.upper())
        if html_elem_attr is not None:
            if "class" in html_elem_attr:
                _class = builder.CLASS(html_elem_attr["class"])
                html_elem_attr.pop("class")
                tag = tag(_class, html_elem_attr)
            else:
                tag = tag(html_elem_attr)
        else:
            tag = tag()
        self._html = tag
