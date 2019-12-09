# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:03
@author: fgiely
"""
import os

from CoreNLG.IterElems import IterElems
from CoreNLG.resources.contraction import contraction

from CoreNLG.AddTag import AddTag
from CoreNLG.Logger import Logger
from CoreNLG.NoInterpret import NoInterpret
from CoreNLG.Number import Number
from CoreNLG.tools import read_json_resource, get_resource_lang, read_default_words


class NlgTools:
    def __init__(
            self,
            html_elem="div",
            html_elem_attr=None,
            active_printers=False,
            log_level="ERROR",
            lang="fr",
            freeze=False,
    ):
        self._lang = lang

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

    def __get_resources(self):
        resource_path = os.path.join(os.path.dirname(__file__), "resources")
        self._ponct = read_json_resource(os.path.join(resource_path, "ponctuation.json"),
                                         self._lang,
                                         self.logger)

        self._default_words = read_json_resource(os.path.join(resource_path, "default_words.json"),
                                                 self._lang,
                                                 self.logger)

        self._contract = get_resource_lang(contraction, self._lang, self.logger)
