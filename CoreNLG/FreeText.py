# -*- coding: utf-8 -*-
"""
created on 09/12/2019 16:15
@author: fgiely
"""
from CoreNLG.PredefObjects import TextVar


class FreeText:
    def free_text(self, *words):
        return TextVar(words)


def free_text(*words):
    return FreeText().free_text(words)
