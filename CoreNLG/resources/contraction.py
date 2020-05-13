# -*- coding: utf-8 -*-
"""
created on 26/06/2019 15:46
@author: fgiely
"""

vowel = ["a", "à", "e", "é", "è", "ê", "i", "î", "o", "u", "y"]
contraction = {
    "fr": {
        "le": {"l'": vowel},
        "la": {"l'": vowel},
        "ce": {"c'": vowel},
        "de": {
            "d'": vowel,
            "du": [("le", "")],
            "des": [("les", "")],
            "duquel": [("lequel", "")],
            "desquels": [("lesquels", "")],
            "desquelles": [("lesquelles", "")],
        },
        "je": {"j'": vowel},
        "me": {"m'": vowel},
        "ne": {"n'": vowel},
        "que": {"qu'": vowel},
        "se": {"s'": vowel},
        "te": {"t'": vowel},
        "puisque": {"puisqu'": ["on", "il"]},
        "lorsque": {"lorsqu'": ["on", "il"]},
        "jusque": {
            "jusqu'": ["à", "en", "alors", "ici", "au", "aux"]
        },
        "à": {
            "au": [("le", "")],
            "aux": [("les", "")],
            "auquel": [("lequel", "")],
            "auxquels": [("lesquels", "")],
            "auxquelles": [("lesquelles", "")],
        },
    },
    "en": {
        "a": {
            "an ": vowel,
        }
    }
}
