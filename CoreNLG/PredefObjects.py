# -*- coding: utf-8 -*-
"""
created on 08/01/2019 10:21
@author: fgiely
"""

interpretable_char = {
    ".": "DOT",
    ",": "COMA",
    '"': "QUOTE",
    "?": "INTERROGATION",
    "!": "EXCLAMATION",
    ":": "DOUBLEDOTS",
    "/": "SLASH",
    " ": "SPACE",
    ";": "SEMICOLON",
    "&": "AMPERSAND",
    "(": "OPENING_PARENTHESIS",
    ")": "CLOSING_PARENTHESIS",
    "<": "LESS_THAN",
    ">": "MORE_THAN",
    "[": "OPENING_BRACKET",
    "]": "CLOSING_BRACKET",
    "\n": "CARRIAGE_RETURN",
}

interpretable_char_reverse = {value: key for key, value in interpretable_char.items()}

class IteratorConstructor:
    def __init__(
            self,
            max_elem=None,
            nb_elem_bullet=None,
            begin_w="",
            end_w="",
            sep=",",
            last_sep="et",
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
        self.text_empty_list = text_if_empty_list
        self.end_of_bullet = end_of_bullet
        self.end_of_last_bullet = end_of_last_bullet


class TextVar(str):
    def __iadd__(self, other):
        f = lambda l: ' '.join([f(x) if type(x) in [list, tuple] else x for x in l if x is not None])
        return TextVar(self + ' ' + f([other])) if self != '' else TextVar(f([other]))
