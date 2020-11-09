# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:03
@author: fgiely
"""
import hashlib
import json
import os
import re

from lxml import html
from lxml import etree

from CoreNLG.FreeText import FreeText
from CoreNLG.Intensity import Intensity
from CoreNLG.IterElems import IterElems
from CoreNLG.Synonyms import Synonyms
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
            thousand_sep=read_default_words(self._default_words, "numbers", "thousand_sep", default=" "),
        ).nlg_num

        self.enum = IterElems(
            sep=read_default_words(self._default_words, "iter_elems", "sep", default=","),
            last_sep=read_default_words(self._default_words, "iter_elems", "last_sep", default="and"),
        ).enum

        self._synonym = Synonyms(freeze)
        self.nlg_syn = self._synonym.synonym
        self.post_eval = self._synonym.post_eval

        self.free_text = FreeText().free_text

        self.intensity = Intensity().intensity

    def __get_resources(self):
        resource_path = os.path.join(os.path.dirname(__file__), "resources")
        self._ponct = read_json_resource(os.path.join(resource_path, "ponctuation.json"), self._lang)
        self._default_words = read_json_resource(os.path.join(resource_path, "default_words.json"), self._lang)
        self._contract = self.__expand_contractions(get_resource_lang(contraction, self._lang))

    def __expand_contractions(self, contracts):
        contract_expended = list()
        for first_word, v in contracts.items():
            secondary = dict()
            first_word = "|".join([first_word, first_word.capitalize()])
            for first_part_replacer, second_word in v.items():
                for second in second_word:
                    if isinstance(second, tuple):
                        second_replacer = second[1]
                        second = "|".join([second[0], second[0].capitalize()])
                    else:
                        second_replacer = second
                        second = "|".join([second, second.capitalize()])
                    secondary.update({(first_word, second): (first_part_replacer, second_replacer)})
            contract_expended.append(secondary)
        return contract_expended

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
            arg = self._synonym.handle_nodes(arg)
            text.append(arg)
            if not no_space:
                text.append(" ")

        text = "".join(text)
        self._text += text
        return text

    def beautify(self, text):
        return beautifier(text, self._ponct, self._contract)

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

    def get_text_details(self, text):
        nodes = self._synonym.get_nodes_in_text(text)
        synonyms = [self._synonym.get_synonym_by_hash(node[1]) for node in nodes if node[0] == "synonym"]
        post_evals = [self._synonym.get_post_eval_by_hash(node[1]) for node in nodes if node[0] == "post-eval"]

        return {
            "text": {
                "raw": self._synonym.replace_tag_by_id(text),
                "beautiful": self.beautify(self._synonym.replace_tag_by_id(text))
            },

            "synonyms": [{
                "id": synonym.non_reg_id if synonym.non_reg_id is not None else synonym.hash,
                "choices": [{
                    "raw": self._synonym.replace_tag_by_id(choice.text),
                    "beautiful": self.beautify(self._synonym.replace_tag_by_id(choice.text)),
                    "keys": list(choice.keys)
                } for choice in sorted(synonym.choices, key=lambda x: x.hash)]
            } for synonym in sorted(synonyms, key=lambda x: x.hash)],

            "post_evals": [{
                "id": post_eval.non_reg_id if post_eval.non_reg_id is not None else post_eval.hash,
                "infos": {
                    "key": post_eval.key,
                    "if_active": {
                        "raw": self._synonym.replace_tag_by_id(post_eval.if_active),
                        "beautiful": self.beautify(self._synonym.replace_tag_by_id(post_eval.if_active))
                    },
                    "if_inactive": {
                        "raw": self._synonym.replace_tag_by_id(post_eval.if_inactive),
                        "beautiful": self.beautify(self._synonym.replace_tag_by_id(post_eval.if_inactive))
                    },
                    "deactivate": post_eval.clean
                }
            } for post_eval in post_evals]
        }

    def get_all_texts(self, text):
        return [self.beautify(combination) for combination in self._synonym.get_all_combinations(text, [])]
