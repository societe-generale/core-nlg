# -*- coding: utf-8 -*-
"""
created on 04/01/2019 11:12
@author: fgiely
"""


class ArgsNotUnpackedError(TypeError):
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return "Text arguments are not unpacked, add * to the list you passed"


class KwargsNotUnpackedError(TypeError):
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return "Text arguments are not unpacked, add * to the list you passed"
