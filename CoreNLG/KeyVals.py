# -*- coding: utf-8 -*-
"""
created on 09/12/2019 14:08
@author: fgiely
"""


class KeyVals:
    def __init__(self):
        self.active_keyvals = []
        self.post_evals = {}
        self.keyval_context = {}

    def post_eval(self, keyval, if_active='', if_inactive='', clean=False):
        # in freeze or random mode, keyval has already be activated
        if keyval in self.active_keyvals:
            return self.handle_post_eval((keyval, if_active, if_inactive, clean))
        else:
            pattern = '~' + str(len(self.post_evals) + 1) + '~'
            self.post_evals[pattern] = (keyval, if_active, if_inactive, clean)
            return pattern

    def handle_post_eval(self, args):
        keyval, if_active, if_inactive, clean = args
        result = if_active if keyval in self.active_keyvals else if_inactive
        self.active_keyvals.remove(keyval) if clean and keyval in self.active_keyvals else None
        return result
