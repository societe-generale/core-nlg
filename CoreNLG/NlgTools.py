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
            thousand_sep=read_default_words(self._default_words, "numbers", "thousand_sep", default=" "),
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
            arg = self._synonym.handle_patterns(arg)
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
        # hash_by_pattern = {}
        id_by_pattern = {}
        patterns = self._synonym.get_found_patterns(text)

        def hash_dict(dict_input):
            return hashlib.sha256(json.dumps(dict_input).encode('utf-8')).hexdigest()

        def replace_pattern_by_hash(text):
            for pattern in id_by_pattern:
                text = text.replace(pattern, id_by_pattern[pattern])
            return text

        def get_id(pattern):
            if pattern[0] in ['*', '%']:
                id = self._synonym.id_by_pattern[pattern]
            else:
                id = self._keyvals.id_by_pattern[pattern]

            if not id:
                id = create_hash(pattern)

            return id

        def create_hash(pattern):
            if pattern[0] in ['*', '%']:
                s_list = []
                for syno in self._synonym.synos_by_pattern[pattern]:
                    beautiful_syno = self.beautify(syno)
                    keys = self._keyvals.keyval_context[pattern].get(syno)
                    try:
                        s_list.append([beautiful_syno, sorted(keys)])
                    except:
                        s_list.append([beautiful_syno, keys])
                s_hash = hash_dict(sorted(s_list, key=lambda x: x[0]))
            else:
                s_hash = hash_dict([
                    self._keyvals.post_evals[pattern][0],
                    self.beautify(self._keyvals.post_evals[pattern][1]),
                    self.beautify(self._keyvals.post_evals[pattern][2]),
                    self._keyvals.post_evals[pattern][3]
                ])

            return s_hash

        def retrieve_all_id(text):
            patterns = [match.group() for match in re.finditer('[*~%][0-9]+[*~%]', text)]
            for pattern in patterns:
                if pattern not in id_by_pattern:
                    if pattern[0] in ['*', '%']:
                        for syno in self._synonym.synos_by_pattern[pattern]:
                            retrieve_all_id(syno)
                        id_by_pattern[pattern] = get_id(pattern)
                    else:
                        for syno in self._keyvals.post_evals[pattern][1:3]:
                            retrieve_all_id(syno)
                        id_by_pattern[pattern] = get_id(pattern)

        retrieve_all_id(text)

        return {
            "text": {
                "raw": replace_pattern_by_hash(text),
                "beautiful": replace_pattern_by_hash(self.beautify(text))
            },
            "synonyms": [{
                "id": id_by_pattern[pattern],
                "choices": [{
                    "raw": replace_pattern_by_hash(syno),
                    "beautiful": replace_pattern_by_hash(self.beautify(syno)),
                    "keys": self._keyvals.keyval_context[pattern].get(syno)
                } for syno in self._synonym.synos_by_pattern[pattern]]
            } for pattern in patterns if pattern[0] in ['*', '%']],
            "post_evals": [{
                "id": id_by_pattern[pattern],
                "infos": {
                    "key": self._keyvals.post_evals[pattern][0],
                    "if_active": {
                        "raw": replace_pattern_by_hash(self._keyvals.post_evals[pattern][1]),
                        "beautiful": replace_pattern_by_hash(self.beautify(self._keyvals.post_evals[pattern][1]))
                    },
                    "if_inactive": {
                        "raw": replace_pattern_by_hash(self._keyvals.post_evals[pattern][2]),
                        "beautiful": replace_pattern_by_hash(self.beautify(self._keyvals.post_evals[pattern][2]))
                    },
                    "deactivate": self._keyvals.post_evals[pattern][3]
                }
            } for pattern in patterns if pattern[0] == '~']
        }

    def get_all_texts(self, text):
        return [self.beautify(combination) for combination in self.__get_all_combinations(text, [])]

    def __get_all_combinations(self, text, active_keys):
        first_node = re.search('[*~%][0-9]+[*~%]', text)

        if first_node is not None:
            pattern = first_node.group()

            if pattern[0] in ['*', '%']:
                choices = []

                for syno in self._synonym.synos_by_pattern[pattern]:
                    try:
                        syno_keys = self._keyvals.keyval_context[pattern][syno]
                    except:
                        syno_keys = []

                    try:
                        choices.append((text.replace(pattern, syno, 1), active_keys + syno_keys))
                    except:
                        choices.append((text.replace(pattern, syno, 1), active_keys + [syno_keys]))

                return [
                    combination for choice in choices for combination in
                    self.__get_all_combinations(choice[0], choice[1])
                ]

            elif pattern[0] == '~':
                key = self._keyvals.post_evals[pattern][0]

                new_text = text.replace(
                    pattern,
                    self._keyvals.post_evals[pattern][1 if key in active_keys else 2],
                    1
                )

                if self._keyvals.post_evals[pattern][3]:
                    active_keys = [k for k in active_keys if k != key]

                return self.__get_all_combinations(new_text, active_keys)

        return [text]
