# -*- coding: utf-8 -*-
"""
created on 02/12/2019 17:30
@author: fgiely
"""
import sys

from lxml import html
from lxml.html import builder

from CoreNLG.tools import handle_string_to_html, temporary_override_args


class IterElems:
    def __init__(
            self,
            max_elem=None,
            nb_elem_bullet=None,
            begin_w=None,
            end_w=None,
            sep="",
            last_sep="",
            capitalize_bullets=True,
            text_if_empty_list="",
            end_of_bullet="",
            end_of_last_bullet=""
    ):

        self.max_elem = max_elem
        self.nb_elem_bullet = nb_elem_bullet
        self.begin_w = begin_w
        self.end_w = end_w
        self.sep = sep
        self.last_sep = last_sep
        self.capitalize_bullets = capitalize_bullets
        self.text_if_empty_list = text_if_empty_list
        self.end_of_bullet = end_of_bullet
        self.end_of_last_bullet = end_of_last_bullet

    @temporary_override_args
    def enum(self,
             pattern,
             max_elem=None,
             nb_elem_bullet=None,
             begin_w=None,
             end_w=None,
             sep=None,
             last_sep=None,
             capitalize_bullets=None,
             text_if_empty_list=None,
             end_of_bullet=None,
             end_of_last_bullet=None):

        if pattern is None:
            return ""
        if isinstance(pattern, list) and len(pattern) > 0 and not isinstance(pattern[0], list):
            pattern = [pattern]
        elem_list = self.__create_list(pattern)
        if len(elem_list) > 0:
            text = list()
            if self.begin_w is not None:
                text.append(str(self.begin_w) + " ")
            if self.nb_elem_bullet is None or len(elem_list) < self.nb_elem_bullet:
                elem = self.__iter_elems(elem_list)
            else:
                elem = self.__bullets_points(elem_list)
            text.append(elem)
            if self.end_w is not None:
                text.append(" " + str(self.end_w))
            return "".join(text)
        else:
            return self.text_if_empty_list

    def __iter_elems(self, iter_elem):
        elem = list()
        if len(iter_elem) == 1:
            return " ".join(iter_elem[0])
        for i in range(len(iter_elem)):
            if i == len(iter_elem) - 2:
                elem += iter_elem[i]
                elem.append(str(self.last_sep))
                elem += iter_elem[i + 1]
                break
            else:
                elem += iter_elem[i]
                elem.append(str(self.sep))
        return " ".join(elem)

    def __bullets_points(self, iter_elem):
        ul = builder.UL()

        i = 0
        for elem in iter_elem:
            elem = " ".join(elem)
            if self.capitalize_bullets:
                elem = "".join([elem[0].upper(), elem[1:]])

            if i == len(iter_elem) - 1:
                elem += str(self.end_of_last_bullet)
            else:
                elem += str(self.end_of_bullet)

            if "<" in elem and ">" in elem:
                elem = html.fromstring(elem)

            ul.append(builder.LI(elem))
            i += 1

        return html.tostring(ul, encoding="utf-8").decode("utf-8")

    def __create_list(self, pattern):
        end = False
        i = 0
        elem_list = list()
        if self.max_elem is None:
            self.max_elem = sys.maxsize
        while not end:
            elem = list()
            # Todo: check iterators are same size
            is_generator = False
            for part in pattern:
                if isinstance(part, str) or isinstance(part, html.HtmlElement) or part is None:
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
        return elem_list[:self.max_elem]


def enum(pattern,
         max_elem=None,
         nb_elem_bullet=None,
         begin_w=None,
         end_w=None,
         sep=None,
         last_sep=None,
         capitalize_bullets=None,
         text_if_empty_list=None,
         end_of_bullet=None,
         end_of_last_bullet=None):
    return IterElems().enum(pattern, **{k: v for k, v in locals().items() if k != "pattern"})
