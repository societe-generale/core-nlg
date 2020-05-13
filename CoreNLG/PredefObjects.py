# -*- coding: utf-8 -*-
"""
created on 08/01/2019 10:21
@author: fgiely
"""


class TextVar(str):
    def __new__(cls, *content):
        drill = lambda l: ' '.join([drill(x) if type(x) in [list, tuple] else str(x) for x in l if x is not None])
        return super().__new__(cls, drill(content))

    def __iadd__(self, other):
        return TextVar(self, ' ', other) if self != '' else TextVar(other)
