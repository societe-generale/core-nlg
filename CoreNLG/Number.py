# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:00
@author: fgiely
"""

from CoreNLG.NoInterpret import NoInterpret
from CoreNLG.tools import take_second_arg_if_first_none, temporary_override_args


class Number:
    def __init__(self, short="", sep=".", mile_sep=" ", thousand_sep=" ", dec: int=None,
                 force_sign=False, remove_trailing_zeros=True, no_interpret=None):

        self.short = short
        self.sep = sep
        self.thousand_sep = thousand_sep if thousand_sep != " " else mile_sep
        self.mile_sep = self.thousand_sep
        self.dec = dec
        self.force_sign = force_sign
        self.remove_trailing_zeros = remove_trailing_zeros
        self.__no_interpret = take_second_arg_if_first_none(no_interpret, NoInterpret().no_interpret)

    @temporary_override_args
    def nlg_num(self, num, short=None, sep=None, mile_sep=None, thousand_sep=None, dec: int=None, force_sign=None, remove_trailing_zeros=None):
        _sign = ""

        if self.force_sign and num > 0:
            _sign = "+"
        if self.dec is None:
            _format = "{}{:,}{}"
        else:
            false_dec = 0
            if self.remove_trailing_zeros:
                num = round(num, self.dec)
                false_dec = self.dec
                false_num = num
                while false_dec > 0:
                    if isinstance(false_num, int) or false_num == int(false_num):
                        break
                    else:
                        false_dec -= 1
                        false_num *= 10
            _format = "{}{:,." + str(self.dec - false_dec) + "f}{}"

        if mile_sep is not None:
            self.thousand_sep = mile_sep
        if thousand_sep is not None:
            self.thousand_sep = thousand_sep
        return self.__no_interpret(
            _format.format(_sign, num, self.short).replace(",", "#THSEP#").replace(".", self.sep).replace("#THSEP#", self.thousand_sep)
        )


def nlg_num(num, short=None, sep=None, mile_sep=None, thousand_sep=None, dec: int=None, force_sign=None, remove_trailing_zeros=None):
    return Number().nlg_num(num, **{k: v for k, v in locals().items() if k != "num"})
