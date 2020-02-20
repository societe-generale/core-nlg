# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:08
@author: fgiely
"""


class AddTag:
    def add_tag(self, tag, text="", _class=None, **kwargs):
        if tag is None:
            return text
        tag = tag.lower()
        _class = "".join([" class=\"", _class, "\""]) if _class is not None else ""
        attribs = ""
        for k, v in kwargs.items():
            attribs += " {}=\"{}\"".format(k, v)

        if isinstance(text, str):
            return "".join(["<", tag, _class, attribs, ">", text, "</", tag, ">"])
        else:
            iter_return = list()
            for t in text:
                iter_return.append("".join(["<", tag, _class, attribs, ">", t, "</", tag, ">"]))
            return list(iter_return)


def add_tag(tag, text="", _class=None, **kwargs):
    return AddTag().add_tag(tag, text, _class, **kwargs)
