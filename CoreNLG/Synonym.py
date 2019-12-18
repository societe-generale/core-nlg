# -*- coding: utf-8 -*-
"""
created on 06/12/2019 16:31
@author: fgiely
"""
import difflib
import random
import re
import string


class Synonym:
    def __init__(self, freeze_syno, keyvals):
        self._freeze_syno = freeze_syno

        self._keyvals = keyvals

        self._synos_written = []
        self.smart_syno_lvl = 0
        self.synos_by_pattern = {}
        self._transco_choice = {}
        self._tmp_choice = {}
        self._text_pos = 0
        self._TAG_RE = re.compile(r"<[^>]+>")

    def synonym(self, *words, mode="smart"):
        s_words = []
        tmp_keyvals = {}
        keyval_context = self._keyvals.keyval_context

        # unpacking arguments if only one element
        if len(words) == 1 and isinstance(words[0], list):
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
                pattern = "*" + str(self.smart_syno_lvl + 1) + "*"

                keyval_context[pattern] = tmp_keyvals

                for pat in [p for word in s_words for p in self.synos_by_pattern if p in word]:
                    if pat in keyval_context:
                        keyval_context[pattern].update(keyval_context[pat])
                        del keyval_context[pat]

                if not keyval_context[pattern]:
                    del keyval_context[pattern]

                self.smart_syno_lvl += 1
                self.synos_by_pattern[pattern] = s_words

                return pattern

    def __handle_synonym(self, pattern_to_evaluate):
        tmp_sbp = self.synos_by_pattern.copy()
        tmp_synos_written = self._synos_written.copy()

        best_evaluation = self.__get_best_leaf(pattern_to_evaluate, tmp_sbp, tmp_synos_written)

        # Updating chosen synonyms
        to_save = ' '.join(best_evaluation.strip().split())
        self._synos_written.append(to_save)

        # Activating keyvals
        self.__activate_keyval_if_any(pattern_to_evaluate, best_evaluation)

        return best_evaluation

    def __activate_keyval_if_any(self, pattern_to_evaluate, syno_chosen):
        keyval_context = self._keyvals.keyval_context
        active_keyvals = self._keyvals.active_keyvals
        if pattern_to_evaluate in keyval_context:
            syno = syno_chosen

            while syno in self._transco_choice:
                previous_branch = self._transco_choice[syno]
                previous_choice = self._tmp_choice[previous_branch]

                pattern_chosen = syno.replace(previous_choice, previous_branch)

                if pattern_chosen in keyval_context[pattern_to_evaluate]:
                    active_keyvals.append(keyval_context[pattern_to_evaluate][pattern_chosen])

                del self._transco_choice[syno]

                syno = previous_choice

            if syno not in self._transco_choice:
                if syno in keyval_context[pattern_to_evaluate]:
                    active_keyvals.append(keyval_context[pattern_to_evaluate][syno])

            del keyval_context[pattern_to_evaluate]

    def __get_best_leaf(self, pattern, sbp, previous_synos):
        """Recursive"""
        for possibility in sbp[pattern]:
            nodes = [pat for pat in sbp if pat in possibility]

            syno_tmp = []
            for pat in nodes:
                best_syno = self.__get_best_leaf(pat, sbp, previous_synos + syno_tmp)
                syno_tmp.append(' '.join(best_syno.strip().split())) if len(nodes) > 1 else None
                possibility = possibility.replace(pat, best_syno)
                self._transco_choice[possibility] = pat

        best_syno = self.__get_best_syno(sbp[pattern], previous_synos)
        self._tmp_choice[pattern] = best_syno

        return best_syno

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

    @staticmethod
    def __get_score(words, previous_synos):
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

    @staticmethod
    def __get_disjoint_sequence(s1, s2):
        s = difflib.SequenceMatcher(None, s1, s2)

        matches = []
        for i, j, n in s.get_matching_blocks():
            matches.append(s1[i:i + n]) if n != 0 else None

        for match in matches:
            if s1.startswith(match) and s2.startswith(match) or s1.endswith(match) and s2.endswith(match):
                s1 = s1.replace(match, '')
                s2 = s2.replace(match, '')

        return s1, s2

    def update_position(self, sentence):
        sentence_without_tag = self._TAG_RE.sub(' ', sentence)
        sentence_without_punct = sentence_without_tag.translate(str.maketrans('', '', string.punctuation))

        nb_words = len([word for word in sentence_without_punct.strip().split() if word != ''])
        self._text_pos += nb_words

    def handle_patterns(self, arg):
        done = False
        post_evals = self._keyvals.post_evals
        while not done:
            first_syno, pos_first_syno = None, None
            first_eval, pos_first_eval = None, None

            for pattern in self.synos_by_pattern:
                pos = arg.find(pattern)
                if pos != -1:
                    first_syno = pattern
                    pos_first_syno = pos
                    break

            for pattern in post_evals:
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
                    del self.synos_by_pattern[first_syno]
                else:
                    arg = arg.replace(first_eval, self._keyvals.handle_post_eval(post_evals[first_eval]))
                    del post_evals[first_eval]
            else:
                done = True

        return arg
