# -*- coding: utf-8 -*-
"""
created on 02/12/2019 16:08
@author: fgiely
"""

from lxml import html
from lxml.html import builder

from CoreNLG.tools import handle_string_to_html


class AddTag:

    def add_tag(self, tag, text="", _class=None, **kwargs):
        """

        :param tag: the HTML container name
        :type tag: string

        :param text:
        :type text: string / list of strings

        :param _class: the value of the attribute 'class' in the container
        :type _class: string

        :param kwargs:
        :return:
        """
        try:
            html_tag = getattr(builder, tag.upper())
        except AttributeError:
            return "tag {} doesn't exist in html".format(tag)
        args = list()
        if _class is not None:
            args.append(builder.CLASS(_class))
        if isinstance(text, str):
            e = handle_string_to_html(html_tag, text, *args, **kwargs)
            return html.tostring(e, encoding="utf-8").decode("utf-8")
        else:
            iter_return = list()
            for t in text:
                e = handle_string_to_html(html_tag, t, *args, **kwargs)
                iter_return.append(html.tostring(e, encoding="utf-8").decode("utf-8"))
            return list(iter_return)


def add_tag(tag, text="", _class=None, **kwargs):
    return AddTag().add_tag(tag, text, _class, **kwargs)
