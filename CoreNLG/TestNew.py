# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:23
@author: fgiely
"""

from CoreNLG.NlgTools import NlgTools
Nlg = NlgTools()
print(Nlg.nlg_num(1111111111))

from CoreNLG.Number import Number
Number = Number()
print(Number.nlg_num(1111111111))

from CoreNLG.Number import nlg_num

print(nlg_num.__doc__)


from CoreNLG.AddTag import add_tag

print(add_tag("p", "banana"))
