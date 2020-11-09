# -*- coding: utf-8 -*-
"""
created on 06/12/2019 16:31
@author: fgiely
"""
import difflib
import random
import re
from copy import deepcopy

from CoreNLG.tools import get_hash


class Synonyms:
    def __init__(self, freeze_syno):
        self._freeze_syno = freeze_syno

        self._synonyms = []
        self._drawn_synonyms = []

        self._active_keys = set()
        self._post_evals = []

        self._node_regex = re.compile('<span class="(synonym|post-eval)" hash="(.*?)"/>')

    def synonym(self, *args, mode="smart", non_reg_id=None):
        def unpack_choice(choice):
            if isinstance(choice, tuple):
                text = choice[0]
                keys = [choice[1]] if isinstance(choice[1], str) else choice[1]
            else:
                text = choice
                keys = []

            return Choice(text, set(keys))

        choices = []
        for arg in args:
            if isinstance(arg, list):
                for choice in arg:
                    choices.append(unpack_choice(choice))
            else:
                choices.append(unpack_choice(arg))

        synonym = Synonym(mode, choices, non_reg_id=non_reg_id)

        # non_reg_id should identify a unique hash
        self.__assert_synonym_id(synonym)

        self._synonyms.append(synonym)
        return synonym.tag

    def post_eval(self, key, if_active='', if_inactive='', clean=False, non_reg_id=None):
        post_eval = PostEval(key, if_active, if_inactive, clean, non_reg_id)

        # non_reg_id should identify a unique hash
        self.__assert_post_eval_id(post_eval)

        self._post_evals.append(post_eval)
        return post_eval.tag

    def handle_nodes(self, arg):
        first_node = re.search(self._node_regex, arg)

        while first_node is not None:
            node_tag, node_type, node_hash = first_node.group(), first_node.group(1), first_node.group(2)

            if node_type == "synonym":
                synonym = self.get_synonym_by_hash(node_hash)
                arg = arg.replace(node_tag, self.__handle_synonym(synonym), 1)
            else:
                post_eval = self.get_post_eval_by_hash(node_hash)
                arg = arg.replace(node_tag, self.__handle_post_eval(post_eval), 1)

            first_node = re.search(self._node_regex, arg)

        return arg

    def __handle_synonym(self, synonym):
        if self._freeze_syno or synonym.mode == "random":
            choice = synonym.choices[0] if self._freeze_syno else random.choice(synonym.choices)
            self._active_keys.update(choice.keys)
            return choice.text
        else:
            res = self.__get_best_leaf(synonym, self._drawn_synonyms, self._active_keys)
            chosen_text, new_keys_state, new_synonyms_drawn = res

            # updating chosen synonyms
            self._drawn_synonyms += [*new_synonyms_drawn, self.__clean_text(chosen_text)]
            # updating active keys
            self._active_keys = new_keys_state

            return chosen_text

    def __get_best_leaf(self, synonym, previous_synos, active_keyvals):
        synonyms_state = {}
        keys_state = {}

        choices = deepcopy(synonym.choices)
        for choice in choices:
            synonyms_state[choice.hash] = deepcopy(previous_synos)
            keys_state[choice.hash] = {*active_keyvals, *choice.keys}

            for node in [match for match in re.finditer(self._node_regex, choice.text)]:
                node_tag, node_type, node_hash = node.group(), node.group(1), node.group(2)

                if node_type == "synonym":
                    synonym = self.get_synonym_by_hash(node_hash)

                    res = self.__get_best_leaf(synonym, synonyms_state[choice.hash], keys_state[choice.hash])
                    chosen_text, new_keys_state, new_synonyms_drawn = res

                    synonyms_state[choice.hash] += [*new_synonyms_drawn, self.__clean_text(chosen_text)]
                    keys_state[choice.hash] = new_keys_state

                    choice.text = choice.text.replace(node_tag, chosen_text)
                else:
                    post_eval = self.get_post_eval_by_hash(node_hash)

                    if post_eval.key in keys_state[choice.hash]:
                        choice.text = choice.text.replace(node_tag, post_eval.if_active)
                    else:
                        choice.text = choice.text.replace(node_tag, post_eval.if_inactive)

                    if post_eval.clean:
                        keys_state[choice.hash] = keys_state[choice.hash].filter(lambda x: x != post_eval.key)

        best_choice = self.__get_best_choice(choices, previous_synos)
        return best_choice.text, keys_state[best_choice.hash], synonyms_state[best_choice.hash]

    def __get_best_choice(self, choices, previous_synos):
        scores = {}
        prev_syns = previous_synos[:]

        done = False
        while not done:
            for choice in choices:
                scores[choice.hash] = self.__get_score(choice.text, prev_syns)

            sorted_scores = sorted(scores.values(), key=lambda x: (x[0], -x[1]), reverse=True)
            max_score = sorted_scores[0]

            result = []
            for key in scores:
                if scores[key] == max_score:
                    result.append([choice for choice in choices if choice.hash == key][0])

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
                return i, len(syno_to_evaluate_words)

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
                return i, similar_words

        return len(previous_synos), 0

    def __handle_post_eval(self, post_eval):
        result = post_eval.if_active if post_eval.key in self._active_keys else post_eval.if_inactive
        if post_eval.clean and post_eval.key in self._active_keys:
            self._active_keys.remove(post_eval.key)
        return result

    def get_synonym_by_hash(self, syno_hash):
        synonyms = [synonym for synonym in self._synonyms if synonym.hash == syno_hash]
        return synonyms[0] if synonyms else None

    def get_post_eval_by_hash(self, post_eval_hash):
        post_evals = [pe for pe in self._post_evals if pe.hash == post_eval_hash]
        return post_evals[0] if post_evals else None

    def get_nodes_in_text(self, text):
        nodes = []
        for node in re.finditer(self._node_regex, text):
            node_tag, node_type, node_hash = node.group(), node.group(1), node.group(2)
            nodes.append((node_type, node_hash))

            if node_type == "synonym":
                synonym = self.get_synonym_by_hash(node_hash)
                for choice in synonym.choices:
                    nodes += self.get_nodes_in_text(choice.text)
            else:
                post_eval = self.get_post_eval_by_hash(node_hash)
                for choice in [post_eval.if_active, post_eval.if_inactive]:
                    nodes += self.get_nodes_in_text(choice)

        return set(nodes)

    def replace_tag_by_id(self, text):
        first_node = re.search(self._node_regex, text)

        while first_node is not None:
            node_tag, node_type, node_hash = first_node.group(), first_node.group(1), first_node.group(2)

            if node_type == "synonym":
                synonym = self.get_synonym_by_hash(node_hash)
                synonym_id = synonym.non_reg_id if synonym.non_reg_id is not None else node_hash
                text = text.replace(node_tag, synonym_id)
            else:
                post_eval = self.get_post_eval_by_hash(node_hash)
                post_eval_id = post_eval.non_reg_id if post_eval.non_reg_id is not None else node_hash
                text = text.replace(node_tag, post_eval_id)

            first_node = re.search(self._node_regex, text)

        return text

    def get_all_combinations(self, text, active_keys):
        first_node = re.search(self._node_regex, text)

        if first_node is not None:
            node_tag, node_type, node_hash = first_node.group(), first_node.group(1), first_node.group(2)

            if node_type == "synonym":
                synonym = self.get_synonym_by_hash(node_hash)

                choices = [{
                    "text": text.replace(node_tag, choice.text, 1),
                    "keys": active_keys + choice.keys
                } for choice in synonym.choices]

                return [
                    combination for choice in choices for combination in
                    self.get_all_combinations(choice['text'], choice['keys'])
                ]

            else:
                post_eval = self.get_post_eval_by_hash(node_hash)

                new_text = text.replace(
                    node_tag,
                    post_eval.if_active if post_eval.key in active_keys else post_eval.if_inactive,
                    1
                )

                if post_eval.clean and post_eval.key in active_keys:
                    active_keys.remove(post_eval.key)

                return self.get_all_combinations(new_text, active_keys)

        return [text]

    def __assert_synonym_id(self, synonym):
        if synonym.non_reg_id is not None:
            for existing_synonym in self._synonyms:
                if existing_synonym.non_reg_id == synonym.non_reg_id:
                    assert existing_synonym.hash == synonym.hash, \
                        f"A different synonym with non_reg_id {synonym.non_reg_id} already exists."

    def __assert_post_eval_id(self, post_eval):
        if post_eval.non_reg_id is not None:
            for pe in self._post_evals:
                if post_eval.non_reg_id == pe.non_reg_id and pe.non_reg_id is not None:
                    assert post_eval.hash == pe.hash, \
                        f"A different post evaluation with non_reg_id {pe.non_reg_id} already exists."

    @staticmethod
    def __clean_text(text):
        return ' '.join(text.strip().split())


class Synonym:
    def __init__(self, mode, choices, non_reg_id=None):
        self.mode = mode
        self.choices = choices
        self.non_reg_id = non_reg_id

        self.hash = get_hash([
            self.mode,
            [choice.hash for choice in sorted(self.choices, key=lambda choice: choice.text)],
            self.non_reg_id]
        )

        self.tag = f'<span class="synonym" hash="{self.hash}"/>'


class Choice:
    def __init__(self, text, keys):
        self.text = text
        self.keys = sorted(keys)
        self.hash = get_hash([self.text, self.keys])


class PostEval:
    def __init__(self, key, if_active, if_inactive, clean, non_reg_id):
        self.key = key
        self.if_active = if_active
        self.if_inactive = if_inactive
        self.clean = clean
        self.non_reg_id = non_reg_id

        self.hash = get_hash([
            self.key,
            self.if_active,
            self.if_inactive,
            self.clean
        ])

        self.tag = f"<span class=\"post-eval\" hash=\"{self.hash}\"/>"
