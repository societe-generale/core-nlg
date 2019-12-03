# -*- coding: utf-8 -*-
"""
created on 02/12/2019 17:30
@author: fgiely
"""
from CoreNLG.PredefObjects import IteratorConstructor
from CoreNLG.decorators import debug_printer


class IterElems:
    def __init__(self):
        pass

    def enum(self, elems, const=None):
        return self.iter_elems([elems], const)

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

