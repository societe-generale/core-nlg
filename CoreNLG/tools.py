# -*- coding: utf-8 -*-
"""
created on 18/12/2018 14:19
@author: fgiely
"""


def levenshtein(word_1, word_2):
    """
        arg :
            listRef         --> list of string(word)
            listComp        --> list of string(word)
        return :
            integer
        Description :
            return the distance between 2 list of string
    """
    char_list_1 = [l for l in word_1]
    char_list_2 = [l for l in word_2]

    if len(char_list_1) == 0:
        return len(char_list_2)
    elif len(char_list_2) == 0:
        return len(char_list_1)
    v0 = [0] * (len(char_list_2) + 1)
    v1 = [0] * (len(char_list_2) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(char_list_1)):
        v1[0] = i + 1
        for j in range(len(char_list_2)):
            cost = 0 if char_list_1[i] == char_list_2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]
    return v1[len(char_list_2)]
