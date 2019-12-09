# -*- coding: utf-8 -*-
"""
created on 08/01/2019 10:21
@author: fgiely
"""


class TextVar(str):
    def __iadd__(self, other):
        f = lambda l: ' '.join([f(x) if type(x) in [list, tuple] else x for x in l if x is not None])
        return TextVar(self + ' ' + f([other])) if self != '' else TextVar(f([other]))
