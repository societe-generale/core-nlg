# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:03
@author: fgiely
"""
import os

from lxml import html
from lxml import etree

from CoreNLG.FreeText import FreeText
from CoreNLG.Intensity import Intensity
from CoreNLG.IterElems import IterElems
from CoreNLG.KeyVals import KeyVals
from CoreNLG.Synonym import Synonym
from CoreNLG.decorators import beautifier
from CoreNLG.resources.contraction import contraction

from CoreNLG.AddTag import AddTag
from CoreNLG.NoInterpret import NoInterpret
from CoreNLG.Number import Number
from CoreNLG.tools import read_json_resource, get_resource_lang, read_default_words


class NlgTools:
    def __init__(self, lang="fr", freeze=False, elem="div", elem_attr=None):
        self._lang = lang
        self.elem = elem
        self.elem_attr = elem_attr
        self._is_beautiful = False
        self._ponct = None
        self._default_words = None
        self._contract = None
        self._text = ""
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

        self._keyvals = KeyVals()
        self.post_eval = self._keyvals.post_eval

        self._synonym = Synonym(freeze, self._keyvals)
        self.nlg_syn = self._synonym.synonym

        self.free_text = FreeText().free_text

        self.intensity = Intensity().intensity

    def __get_resources(self):
        resource_path = os.path.join(os.path.dirname(__file__), "resources")
        self._ponct = read_json_resource(os.path.join(resource_path, "ponctuation.json"), self._lang)
        self._default_words = read_json_resource(os.path.join(resource_path, "default_words.json"), self._lang)
        self._contract = get_resource_lang(contraction, self._lang)

    def __str__(self):
        self.__beautifier()
        return self._text

    @property
    def text(self):
        self.__beautifier()
        return self._text

    def write_text(self, *args, no_space=False):
        """Creates a list of string"""
        self._is_beautiful = False
        text = list()
        for arg in args:
            arg = self._synonym.handle_patterns(arg)
            text.append(arg)
            if not no_space:
                text.append(" ")

        self._synonym.smart_syno_lvl = 0
        self._synonym.synos_by_pattern = {}
        text = "".join(text)
        self._text += text
        return text

    def __beautifier(self):
        """

        :return:
        """
        if not self._is_beautiful:
            self._text = beautifier(self._text, self._ponct, self._contract)
            self._is_beautiful = True
        return self._text

    @property
    def html(self):
        if self.elem_attr is None or len(self.elem_attr) == 0:
            return html.fromstring(self.add_tag(self.elem, self.text))
        return html.fromstring(self.add_tag(self.elem, self.text, **self.elem_attr))

    @property
    def xml(self):
        if self.elem_attr is None or len(self.elem_attr) == 0:
            return etree.fromstring(self.add_tag(self.elem, self.text))
        return etree.fromstring(self.add_tag(self.elem, self.text, **self.elem_attr))

