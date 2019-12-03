# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:00
@author: fgiely
"""
from CoreNLG.NoInterpret import NoInterpret
from CoreNLG.tools import take_second_arg_first_none


class Number:
    def __init__(self, short="", sep=".", mile_sep=" ", dec=None,
                 force_sign=False, remove_trailing_zeros=True, no_interpret=None):
        self.__short = short
        self.__sep = sep
        self.__mile_sep = mile_sep
        self.__dec = dec
        self.__force_sign = force_sign
        self.__force_sign = force_sign
        self.__remove_trailing_zeros = remove_trailing_zeros
        self.__no_interpret = take_second_arg_first_none(no_interpret, NoInterpret().no_interpret)

    def nlg_num(self, num, short=None, sep=None, mile_sep=None, dec=None, force_sign=None, remove_trailing_zeros=None):
        _sign = ""
        
        short = take_second_arg_first_none(short, self.__short)
        sep = take_second_arg_first_none(sep, self.__sep)
        mile_sep = take_second_arg_first_none(mile_sep, self.__mile_sep)
        dec = take_second_arg_first_none(dec, self.__dec)
        force_sign = take_second_arg_first_none(force_sign, self.__force_sign)
        remove_trailing_zeros = take_second_arg_first_none(remove_trailing_zeros, self.__remove_trailing_zeros)

        if force_sign and num > 0:
            _sign = "+"
        if dec is None:
            _format = "{}{:,}{}"
        else:
            false_dec = 0
            if remove_trailing_zeros:
                num = round(num, dec)
                false_dec = dec
                false_num = num
                while false_dec > 0:
                    if isinstance(false_num, int) or false_num == int(false_num):
                        break
                    else:
                        false_dec -= 1
                        false_num *= 10
            _format = "{}{:,." + str(dec - false_dec) + "f}{}"
        return self.__no_interpret(
            _format.format(_sign, num, short).replace(",", mile_sep).replace(".", sep)
        )


def nlg_num(num, short="", sep=".", mile_sep=" ", dec: int=None, force_sign=False, remove_trailing_zeros=True):
    """

    cihseguie

    :param num:
    :param short:
    :param sep:
    :param mile_sep:
    :param dec:
    :param force_sign:
    :param remove_trailing_zeros:
    :return:
    """
    return Number().nlg_num(num, short, sep, mile_sep, dec, force_sign, remove_trailing_zeros)
