# -*- coding: utf-8 -*-
"""
created on 18/12/2018 14:19
@author: fgiely
"""
import functools
import hashlib
import json
import os

from lxml import html


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


def handle_string_to_html(html_tag, text, *args, **kwargs):
    """
    If the text contains HTML elements, adds them inside the HTML tag created with the builder 'html_tag'.
    If it contains a string not in a HTML element, then it becomes the text content of the HTML tag.

    :param html_tag: builder of the HTML tag
    :type html_tag: lxml.html.builder function

    :param text: the text of the HTML tag
    :type text: string

    :param args: the class of the HTML container
    :type args: None / string / list of strings

    :param kwargs: other attributes of the HTML container
    :type kwargs: None / string / list of strings

    :return: the final element correctly formatted, especially if there was HTML containers in the text
    :return type: HTML element (lxml.html.HtmlElement)
    """

    e = html_tag(*args, **kwargs)
    e.text = ""
    for elem in html.fragments_fromstring(text):
        if isinstance(elem, str):
            e.text += elem
        else:
            e.append(elem)
    return e


def take_second_arg_if_first_none(arg, class_arg):
    return class_arg if arg is None else arg


def read_json_resource(path, lang):
    with open(os.path.join(path), encoding="utf-8") as f:
        return get_resource_lang(json.load(f)["lang"], lang)


def get_resource_lang(resource, lang):
    try:
        return resource[lang]
    except KeyError:
        raise Exception("lang \"{}\" doesn't exist in ponctuation resource".format(lang))


def read_default_words(resource, *args, default=""):
    for a in args:
        try:
            resource = resource[a]
        except KeyError:
            return default
    return resource if resource is not None else default


def temporary_override_args(f):
    @functools.wraps(f)
    def temporary_override_f(*args, **kwargs):
        tmp = {}
        for k, v in kwargs.items():
            if v is not None:
                class_value = getattr(args[0], k)
                tmp.update({k: class_value})
                setattr(args[0], k, v)
        f_value = f(*args, **kwargs)
        for k, v in tmp.items():
            setattr(args[0], k, v)
        return f_value

    return temporary_override_f


def get_hash(to_hash):
    return hashlib.sha256(json.dumps(to_hash).encode('utf-8')).hexdigest()
