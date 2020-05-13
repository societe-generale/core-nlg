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

        if self._freeze_syno or mode == 'random':
            syno_to_display = s_words[0] if self._freeze_syno else random.choice(s_words)
            if syno_to_display in tmp_keyvals:
                self._keyvals.active_keyvals.append(tmp_keyvals[syno_to_display])
            return syno_to_display
        else:
            pattern = "*" + str(self.smart_syno_lvl + 1) + "*"

            keyval_context[pattern] = tmp_keyvals

            self.smart_syno_lvl += 1
            self.synos_by_pattern[pattern] = s_words

            return pattern

    def __handle_synonym(self, pattern):
        c_sbp = self.synos_by_pattern.copy()
        c_prev_syn = self._synos_written.copy()
        c_active_keys = self._keyvals.active_keyvals.copy()

        draw_syn, active_keys, drawn_syns_in_tree = self.__get_best_leaf(pattern, c_sbp, c_prev_syn, c_active_keys)

        # Updating chosen synonyms
        clean_syn = ' '.join(draw_syn.strip().split())
        self._synos_written += drawn_syns_in_tree + [clean_syn]

        # Activating keyvals
        self._keyvals.active_keyvals = active_keys

        return clean_syn

    def __get_best_leaf(self, pattern, sbp, previous_synos, active_keyvals):
        kv_context = self._keyvals.keyval_context

        keyvals = []
        synos_tmp = []
        for i, choice in enumerate(sbp[pattern]):
            # syno_tmp = []
            keyvals.append(active_keyvals.copy())
            synos_tmp.append([])

            # temporary activation of the keyvals for this choice
            if pattern in kv_context and choice in kv_context[pattern]:
                keys = kv_context[pattern][choice]
                if type(keys) is not list:
                    keys = [keys]
                keyvals[i] += [key for key in keys if key not in keyvals[i]]

            node_list = [match.group() for match in re.finditer('[*~][0-9]+[*~]', choice)]
            for node in node_list:

                is_post_eval = node[0] == '~'

                if is_post_eval:
                    key, if_active, if_inactive, clean = self._keyvals.post_evals[node]
                    sbp[pattern][i] = sbp[pattern][i].replace(node, if_active if key in keyvals[i] else if_inactive)
                    keyvals[i].remove(key) if clean and key in keyvals[i] else None
                else:
                    prev_syns = previous_synos + synos_tmp[i]
                    drawn_syn, kv, syns_in_tree = self.__get_best_leaf(node, sbp, prev_syns, keyvals[i])
                    synos_tmp[i].append(' '.join(drawn_syn.strip().split()))
                    sbp[pattern][i] = sbp[pattern][i].replace(node, drawn_syn)
                    keyvals[i] = kv

        best_syno = self.__get_best_syno(sbp[pattern], previous_synos)
        index_best_syno = sbp[pattern].index(best_syno)
        return best_syno, keyvals[index_best_syno], synos_tmp[index_best_syno]

    def __get_best_syno(self, synos, previous_synos):
        scores = {}
        done = False
        prev_syns = previous_synos.copy()
        result = []

        while not done:
            for syno in synos:
                scores[syno] = self.__get_score(syno, prev_syns)

            sorted_scores = sorted(scores.values(), key=lambda x: (x[0], -x[1]), reverse=True)
            max_score = sorted_scores[0]

            result = []
            for key in scores:
                if scores[key] == max_score:
                    result.append(key)

            prev_syns = prev_syns[:-max_score[0] - 1]
            done = len(result) == 1 or not prev_syns

        return random.choice(result)

    @staticmethod
    def __get_score(syno_to_evaluate, previous_synos):
        """
        - 2 words are considered similar if more than 'word_similarity_threshold' % of one word is in the other one
        - 2 synonyms are considered similar if one of them has more than 'syno_similarity_threshold' % of similar words with the other one
        """
        min_length_following_letters = 3
        word_similarity_threshold = 0.6
        syno_similarity_threshold = 0.25
        significant_word_length = 3

        syno_to_evaluate_words = [w for w in syno_to_evaluate.split() if len(w) >= significant_word_length]

        for i, previous_synonym in enumerate(reversed(previous_synos)):
            if syno_to_evaluate == previous_synonym:
                return (i, len(syno_to_evaluate_words))

            previous_syno_words = [w for w in previous_synonym.split() if len(w) >= significant_word_length]
            if not syno_to_evaluate_words or not previous_syno_words:
                continue

            similar_words = 0
            for w_1 in previous_syno_words:
                for w_2 in syno_to_evaluate_words:
                    matching_blocks = difflib.SequenceMatcher(None, w_1, w_2).get_matching_blocks()
                    n_following_letters = sum(bl[2] for bl in matching_blocks if bl[2] >= min_length_following_letters)
                    if n_following_letters >= max(len(w_1), len(w_2)) * word_similarity_threshold:
                        similar_words += 1

            if similar_words >= max(len(previous_syno_words), len(syno_to_evaluate_words)) * syno_similarity_threshold:
                return (i, similar_words)

        return (len(previous_synos), 0)

    def handle_patterns(self, arg):
        first_node = re.search('[*~][0-9]+[*~]', arg)

        while first_node is not None:
            node = first_node.group()

            if node[0] == '~':
                arg = arg.replace(node, self._keyvals.handle_post_eval(self._keyvals.post_evals[node]))
            else:
                arg = arg.replace(node, self.__handle_synonym(node))

            first_node = re.search('[*~][0-9]+[*~]', arg)

        return arg
