# -*- coding: utf-8 -*-
"""
created on 09/12/2019 16:15
@author: fgiely
"""


class FreeText:
    def free_text(self, *words):
        text = list()
        for word in words:
            if isinstance(word, list) or isinstance(word, tuple):
                text.append(" ".join([self.free_text(w) for w in word if w is not None]))
            elif word is not None:
                text.append(word)
        return " ".join(text)


def free_text(*words):
    return FreeText().free_text(words)
