# -*- coding: utf-8 -*-
"""
created on 18/12/2018 17:09
@author: fgiely
"""
import json
import string
import os
import sys
import lxml
import random
import difflib
import re

from CoreNLG.Logger import Logger
from lxml import html
from lxml.html import builder
from CoreNLG.PredefObjects import IteratorConstructor, interpretable_char
from CoreNLG.decorators import debug_printer, beautifier
from CoreNLG.resources.contraction import contraction


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
        self._html = None
        self.__html_elem_wrap(html_elem, html_elem_attr)
        self.active_all_printers = active_printers
        self._log_level = log_level
        self._log = Logger(os.path.join(os.getcwd(), "logs"), self._log_level)
        self.logger = self._log.logger

        # For synonyms
        self._freeze_syno = freeze
        self._synos_written = []
        self._smart_syno_lvl = 0
        self._synos_by_pattern = {}
        self.tmp_choice = {}
        self.transco_choice = {}
        self._text_pos = 0
        self._TAG_RE = re.compile(r"<[^>]+>")

        # For keyvals
        self.active_keyvals = []
        self.post_evals = {}
        self.keyval_context = {}

        self._is_beautiful = False
        self._lang = lang

        with open(
                os.path.join(os.path.dirname(__file__), "resources/ponctuation.json")
        ) as f:
            try:
                self._ponct = json.load(f)["lang"][self._lang]
            except KeyError:
                self.logger.error("lang \"{}\" doesn't exist in ponctuation resource".format(self._lang))
                exit(1)

        try:
            self._contract = contraction[self._lang]
        except KeyError:
            self.logger.error("lang \"{}\" doesn't exist in contraction resource".format(self._lang))
            exit(1)

        with open(
                os.path.join(os.path.dirname(__file__), "resources/default_words.json")
        ) as f:
            try:
                self._default_words = json.load(f)["lang"][self._lang]
            except KeyError:
                self.logger.error("lang \"{}\" doesn't exist in default_words resource".format(self._lang))
                exit(1)

    def __str__(self):
        self.beautifier()
        return lxml.html.tostring(
            self._html, pretty_print=True, encoding="utf-8"
        ).decode("utf-8")

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

    @property
    def html(self):
        """
        Ca
        :return:
        """
        self.beautifier()
        return self._html

    @property
    def html_str(self):
        self.beautifier()
        return lxml.html.tostring(
            self._html, pretty_print=True, encoding="utf-8"
        ).decode("utf-8")

    @debug_printer
    def write_text(self, *args, no_space=False):
        """Creates a list of string"""
        self._is_beautiful = False
        text = list()
        for arg in args:

            arg = self.__handle_patterns(arg)
            self.__update_position(arg)

            text.append(arg)
            if not no_space:
                text.append(" ")

        self._smart_syno_lvl = 0
        self._synos_by_pattern = {}
        span = self.__handle_string_to_html(
            builder.SPAN, "".join(text), builder.CLASS("to_delete")
        )
        self._html.append(span)
        return span

    def __update_position(self, sentence):
        sentence_without_tag = self._TAG_RE.sub(' ', sentence)
        sentence_without_punct = sentence_without_tag.translate(str.maketrans('', '', string.punctuation))

        nb_words = len([word for word in sentence_without_punct.strip().split() if word != ''])
        self._text_pos += nb_words

    def __handle_patterns(self, arg):
        done = False
        while not done:
            first_syno, pos_first_syno = None, None
            first_eval, pos_first_eval = None, None

            for pattern in self._synos_by_pattern:
                pos = arg.find(pattern)
                if pos != -1:
                    first_syno = pattern
                    pos_first_syno = pos
                    break

            for pattern in self.post_evals:
                pos = arg.find(pattern)
                if pos != -1:
                    first_eval = pattern
                    pos_first_eval = pos
                    break

            is_syno = False
            first = None

            if first_syno and first_eval:
                if pos_first_syno < pos_first_eval:
                    first = first_syno
                    is_syno = True
                else:
                    first = first_eval
                    is_syno = False
            elif first_syno:
                first = first_syno
                is_syno = True
            elif first_eval:
                first = first_eval
                is_syno = False

            if first:
                if is_syno:
                    pos_end_pattern = pos_first_syno + len(first_syno)
                    text_to_analyze = arg[:pos_end_pattern]
                    following_text = arg[pos_end_pattern:]
                    analyzed_text = text_to_analyze.replace(first_syno, self.__handle_synonym(first_syno))
                    arg = analyzed_text + following_text
                    del self._synos_by_pattern[first_syno]
                else:
                    arg = arg.replace(first_eval, self.__handle_post_eval(self.post_evals[first_eval]))
                    del self.post_evals[first_eval]
            else:
                done = True

        return arg

    def beautifier(self):
        """

        :return:
        """
        if not self._is_beautiful:
            for span in self._html.xpath("//span[@class='to_delete']"):
                span.drop_tag()
            text = lxml.html.tostring(self._html, encoding="utf-8").decode("utf-8")
            self._html = lxml.html.fromstring(
                beautifier(text, self._ponct, self._contract)
            )
            self._is_beautiful = True
        return self._html

    @debug_printer
    def conjug(self, *args, tense="PRESENT"):
        # TODO NLU conjug
        if tense == "PRESENT":
            print("conjug au présent")
        text = list()
        for arg in args:
            for word in arg.split(" "):
                text.append(word)
        return " ".join(text)

    @debug_printer
    def simple_conjug(self, pers=None, verb=None, tense="PRESENT"):
        # TODO conjug verb
        return verb

    @debug_printer
    def free_text(self, *words):
        text = list()
        for word in words:
            if isinstance(word, list) or isinstance(word, tuple):
                text.append(" ".join([self.free_text(w) for w in word if w is not None]))
            elif word is not None:
                text.append(word)
        return " ".join(text)

    @staticmethod
    def __iter_elems(iter_elem, const):
        elem = list()
        if len(iter_elem) == 1:
            return " ".join(iter_elem[0])
        for i in range(len(iter_elem)):
            if i == len(iter_elem) - 2:
                elem += iter_elem[i]
                elem.append(const.last_sep)
                elem += iter_elem[i + 1]
                break
            else:
                elem += iter_elem[i]
                elem.append(const.sep)
        return " ".join(elem)

    def __bullets_points(self, iter_elem, const):
        ul = builder.UL()

        i = 0
        for elem in iter_elem:
            elem = " ".join(elem)
            if const.capitalize_bullets:
                elem = "".join([elem[0].upper(), elem[1:]])

            if i == len(iter_elem) - 1:
                elem += const.end_of_last_bullet
            else:
                elem += const.end_of_bullet

            if "<" in elem and ">" in elem:
                elem = self.__handle_string_to_html(builder.SPAN, elem, builder.CLASS("to_delete"))

            ul.append(builder.LI(elem))
            i += 1

        return html.tostring(ul, encoding="utf-8").decode("utf-8")

    @staticmethod
    def __create_list(pattern, const):
        end = False
        i = 0
        elem_list = list()
        if const.max_elem is None:
            const.max_elem = sys.maxsize
        while not end:
            elem = list()
            # Todo: check iterators are same size
            is_generator = False
            for part in pattern:
                if isinstance(part, str) or isinstance(part, lxml.html.HtmlElement) or part is None:
                    if part is not None and part != "":
                        elem.append(part)
                else:
                    is_generator = True
                    try:
                        if isinstance(part, list):
                            e = part[i]
                        else:
                            e = next(part)
                    except (IndexError, StopIteration):
                        end = True
                        break
                    if e is not None and e != "":
                        elem.append(e)
            if not end and elem is not None and len(elem) > 0:
                elem_list.append(elem)
            if not is_generator:
                end = True
            i += 1
        return elem_list[:const.max_elem]

    @debug_printer
    def iter_elems(self, pattern, const=None):
        if pattern is None:
            return ""
        if const is None:
            const = IteratorConstructor(last_sep=self._default_words["last_sep"])
        elem_list = self.__create_list(pattern, const)
        if len(elem_list) > 0:
            text = list()
            if const.begin_w != "":
                text.append(const.begin_w + " ")
            if const.nb_elem_bullet is None or len(elem_list) < const.nb_elem_bullet:
                elem = self.__iter_elems(elem_list, const)
            else:
                elem = self.__bullets_points(elem_list, const)
            text.append(elem)
            if const.end_w != "":
                text.append(" " + const.end_w)
            return "".join(text)
        else:
            return const.text_empty_list

    def enum(self, elems, const=None):
        return self.iter_elems([elems], const)

    @debug_printer
    def add_tag(self, tag, text="", _class=None, **kwargs):
        """

        :param tag: the HTML container name
        :type tag: string

        :param text:
        :type text: string / list of strings

        :param _class: the value of the attribute 'class' in the container
        :type _class: string

        :param kwargs:
        :return:
        """
        try:
            html_tag = getattr(builder, tag.upper())
        except AttributeError:
            return "tag {} doesn't exist in html".format(tag)
        args = list()
        if _class is not None:
            args.append(builder.CLASS(_class))
        if isinstance(text, str):
            e = self.__handle_string_to_html(html_tag, text, *args, **kwargs)
            return html.tostring(e, encoding="utf-8").decode("utf-8")
        else:
            iter_return = list()
            for t in text:
                e = self.__handle_string_to_html(html_tag, t, *args, **kwargs)
                iter_return.append(html.tostring(e, encoding="utf-8").decode("utf-8"))
            return list(iter_return)

    @staticmethod
    def __handle_string_to_html(html_tag, text, *args, **kwargs):
        """
        If the text contains HTML elements, adds them inside the HTML tag created with the builder 'html_tag'.
        If it contains a string not in a HTML element, then it becomes the text content of the HTML tag.

        :param html_tag: builder of the HTML tag
        :type html_tag: lxml.html.builder function

        :param text: the text of the HTML tag
        :type text: string

        :param args: the class of the HTML container
        :type args: None / string / list of strings

        :param kwargs: other attributes of the HTML container
        :type kwargs: None / string / list of strings

        :return: the final element correctly formatted, especially if there was HTML containers in the text
        :return type: HTML element (lxml.html.HtmlElement)
        """

        e = html_tag(*args, **kwargs)
        e.text = ""
        for elem in html.fragments_fromstring(text):
            if isinstance(elem, str):
                e.text += elem
            else:
                e.append(elem)
        return e

    @staticmethod
    def __no_interpret_char(char):
        try:
            return "".join(["#", interpretable_char[char], "#"])
        except KeyError:
            return char

    @debug_printer
    def no_interpret(self, text):
        not_interpret_text = "".join([self.__no_interpret_char(c) for c in text])
        if '  ' in text:
            return self.add_tag("span", not_interpret_text, style="white-space:pre")
        else:
            return not_interpret_text

    @debug_printer
    def number(self, num, short="", sep=".", mile_sep=" ", dec=None, force_sign=False, remove_trailing_zeros=True):

        # todo : changer texte grands nombres ( 1 000 millions de milliard au lieu de 1 000M)
        _sign = ""
        if force_sign and num > 0:
            _sign = "+"
        if dec is None:
            _format = "{}{:,}{}"
        else:
            false_dec = 0
            if remove_trailing_zeros:
                num = round(num, dec)
                false_dec = dec
                false_num = num
                while false_dec > 0:
                    if isinstance(false_num, int) or false_num == int(false_num):
                        break
                    else:
                        false_dec -= 1
                        false_num *= 10
            _format = "{}{:,." + str(dec - false_dec) + "f}{}"
        return self.no_interpret(
            _format.format(_sign, num, short).replace(",", mile_sep).replace(".", sep)
        )

    @staticmethod
    def intensity(num, intensity_def):
        print(intensity_def)
        for i, thresh in enumerate(intensity_def["threshold"]):
            if num < thresh:
                return intensity_def["intensity"][i]
        return intensity_def["intensity"][-1]

    @debug_printer
    def synonym(self, *words, mode="smart"):
        s_words = []
        tmp_keyvals = {}

        # unpacking arguments if only one element
        if len(words) == 1:
            words = words[0]

        for word in words:
            if type(word) is tuple:
                s_words.append(word[0])
                tmp_keyvals[word[0]] = word[1]
            elif type(word) is list:
                for w in word:
                    s_words.append(w)
            else:
                s_words.append(word)

        if self._freeze_syno:
            return s_words[0]
        else:
            if mode == "random":
                return random.choice(s_words)
            else:
                pattern = "*" + str(self._smart_syno_lvl + 1) + "*"

                self.keyval_context[pattern] = tmp_keyvals

                for pat in [p for word in s_words for p in self._synos_by_pattern if p in word]:
                    if pat in self.keyval_context:
                        self.keyval_context[pattern].update(self.keyval_context[pat])
                        del self.keyval_context[pat]

                if not self.keyval_context[pattern]:
                    del self.keyval_context[pattern]

                self._smart_syno_lvl += 1
                self._synos_by_pattern[pattern] = s_words

                return pattern

    def __handle_synonym(self, pattern_to_evaluate):
        tmp_sbp = self._synos_by_pattern.copy()
        tmp_synos_written = self._synos_written.copy()

        best_evaluation = self.__get_best_leaf(pattern_to_evaluate, tmp_sbp, tmp_synos_written)

        # Updating chosen synonyms
        to_save = ' '.join(best_evaluation.strip().split())
        self._synos_written.append(to_save)

        # Activating keyvals
        self.__activate_keyval_if_any(pattern_to_evaluate, best_evaluation)

        return best_evaluation

    def __activate_keyval_if_any(self, pattern_to_evaluate, syno_chosen):
        if pattern_to_evaluate in self.keyval_context:
            syno = syno_chosen

            while syno in self.transco_choice:
                previous_branch = self.transco_choice[syno]
                previous_choice = self.tmp_choice[previous_branch]

                pattern_chosen = syno.replace(previous_choice, previous_branch)

                if pattern_chosen in self.keyval_context[pattern_to_evaluate]:
                    self.active_keyvals.append(self.keyval_context[pattern_to_evaluate][pattern_chosen])

                del self.transco_choice[syno]

                syno = previous_choice

            if syno not in self.transco_choice:
                if syno in self.keyval_context[pattern_to_evaluate]:
                    self.active_keyvals.append(self.keyval_context[pattern_to_evaluate][syno])

            del self.keyval_context[pattern_to_evaluate]

    def __get_best_leaf(self, pattern, sbp, previous_synos):
        """Recursive"""
        for possibility in sbp[pattern]:
            nodes = [pat for pat in sbp if pat in possibility]

            syno_tmp = []
            for pat in nodes:
                best_syno = self.__get_best_leaf(pat, sbp, previous_synos + syno_tmp)
                syno_tmp.append(' '.join(best_syno.strip().split())) if len(nodes) > 1 else None
                possibility = possibility.replace(pat, best_syno)
                self.transco_choice[possibility] = pat

        best_syno = self.__get_best_syno(sbp[pattern], previous_synos)
        self.tmp_choice[pattern] = best_syno

        return best_syno

    @debug_printer
    def post_eval(self, keyval, if_active='', if_inactive='', clean=False):
        pattern = '~' + str(len(self.post_evals) + 1) + '~'
        self.post_evals[pattern] = (keyval, if_active, if_inactive, clean)
        return pattern

    def __handle_post_eval(self, args):
        keyval, if_active, if_inactive, clean = args
        result = if_active if keyval in self.active_keyvals else if_inactive
        self.active_keyvals.remove(keyval) if clean and keyval in self.active_keyvals else None
        return result

    def __get_best_syno(self, synos, previous_synos):
        scores = {}
        last_occ = {}
        for word in synos:
            scores[word] = 0
            last_occ[word] = 0

        for syno in synos:
            scores[syno] = self.__get_score(syno, previous_synos)

        min_score = scores[min(scores, key=scores.get)]

        result = []
        for key in scores:
            if scores[key] == min_score:
                result.append(key)

        return random.choice(result)

    def __get_score(self, words, previous_synos):
        occ = 0
        last_pos = 0
        pos = len(previous_synos)

        for syno_words in previous_synos:
            found = False
            split_synos = syno_words.split() if syno_words != '' else ['']

            for s_word in split_synos:
                split_words = words.split() if words != '' else ['']

                for word in split_words:
                    is_significant_word = len(word) > 2 or word == ''
                    ratio = difflib.SequenceMatcher(None, s_word, word).quick_ratio() if is_significant_word else 0

                    if ratio > 0.7:
                        found = True
                        occ += 1

            last_pos = pos if found else last_pos
            pos -= 1

        if len([word for word in words.split() if len(word) > 2]) > 1:
            occ /= len(words.split()) / 2

        dist = last_pos

        return 0 if occ == 0 else (occ * occ) / (dist * dist) if dist != 0 else 1

    def __get_disjoint_sequence(self, s1, s2):
        s = difflib.SequenceMatcher(None, s1, s2)

        matches = []
        for i, j, n in s.get_matching_blocks():
            matches.append(s1[i:i + n]) if n != 0 else None

        for match in matches:
            if s1.startswith(match) and s2.startswith(match) or s1.endswith(match) and s2.endswith(match):
                s1 = s1.replace(match, '')
                s2 = s2.replace(match, '')

        return s1, s2
