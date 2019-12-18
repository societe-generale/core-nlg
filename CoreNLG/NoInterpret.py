# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:07
@author: fgiely
"""
from CoreNLG.AddTag import AddTag
from CoreNLG.tools import take_second_arg_if_first_none

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


class NoInterpret:
    interpretable_char = interpretable_char

    interpretable_char_reverse = interpretable_char_reverse

    def __init__(self, add_tag=None):
        self.__add_tag = take_second_arg_if_first_none(add_tag, AddTag().add_tag)

    def __no_interpret_char(self, char):
        try:
            return "".join(["#", self.interpretable_char[char], "#"])
        except KeyError:
            return char

    def no_interpret(self, text):
        not_interpret_text = "".join([self.__no_interpret_char(c) for c in text])
        if '  ' in text:
            return self.__add_tag("span", not_interpret_text, style="white-space:pre")
        else:
            return not_interpret_text


def no_interpret(text):
    return NoInterpret().no_interpret(text)
