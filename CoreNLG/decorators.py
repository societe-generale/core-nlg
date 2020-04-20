# -*- coding: utf-8 -*-
"""
created on 18/12/2018 11:35
@author: fgiely
"""
import copy
import functools
import re

from lxml import html

from CoreNLG import Errors
from CoreNLG.NoInterpret import interpretable_char_reverse


def handle_capitalize(splitters, *args):

    capitalized_text = list()
    for i, a in enumerate(args):
        new_string = a
        matchs = list()
        if i == 0:
            match = re.search("".join([r"^", balise_regex(), r"*( *\n*)*[a-z]"]), new_string)
            if match is not None:
                matchs.append(match)
        matchs += re.finditer("".join(["(\\" + "|\\".join(splitters), ")( *\n*)*", balise_regex(), "*( *\n*)*[a-z]"]), new_string)
        for match in matchs:
            new_string = new_string[:match.span()[1] - 1] + new_string[match.span()[1] - 1].upper() + new_string[match.span()[1]:]
        capitalized_text.append(new_string)
    return capitalized_text


def new_contraction(text, contract):
    re_contract = False
    for first_word, v in contract.items():
        first_word = "|".join([first_word, first_word.capitalize()])
        candidats = list()
        for first_part_replacer, second_word in v.items():

            for second in second_word:
                if isinstance(second, tuple):
                    second_replacer = second[1]
                    second = "|".join([second[0], second[0].capitalize()])
                else:
                    second_replacer = second
                    second = "|".join([second, second.capitalize()])
                for match in re.finditer("".join(["(([^a-zA-Z]+|^))(", first_word, ")(<[^>]*>)*([^<a-zA-Z])+(", second, ")"]), text):
                    replacer = list()
                    for g in match.groups():
                        replacer.append(g if g is not None else "")
                    replacer[2] = first_part_replacer
                    replacer[-1] = second_replacer.capitalize() if replacer[-1][0].isupper() else second_replacer
                    replacer.pop(0)
                    candidats.append((match.group(), replacer))
        if len(candidats) > 0:
            candidats.sort(key=lambda t: len(t[0]), reverse=True)
            text = re.sub(candidats[0][0], "".join(candidats[0][1]), text)
            re_contract = True
    if re_contract:
        text = new_contraction(text, contract)
    return text


def handle_dots(text):
    matchs = re.finditer("".join([r"\.+(", balise_regex(), r"*([^a-zA-Z0-1])*)*\.+"]), text)
    nb_removed = 0
    re_check = False
    for match in matchs:
        nb_dots = len(re.findall(r"\.", match.group()))
        if nb_dots == 2 or nb_dots > 3:
            if nb_dots > 3:
                re_check = True
            text = text[:match.span()[1] - 1 - nb_removed] + text[match.span()[1] - nb_removed:]
            nb_removed += 1
        elif nb_dots == 3:
            text, nb_removed = remove_match_spaces(text, match, nb_removed)
    if re_check:
        text = handle_dots(text)
    return text


def remove_spaces_before(text, char, keep_one=False):
    new_text = text

    for inner_match in re.finditer(">[^<]+", text):
        nb_removed = 0
        inner_text = inner_match.group()
        inner_text_spaces = inner_text.replace(char, " " + char)
        for match in re.finditer("".join([" *\\", char]), inner_text_spaces):
            inner_text_spaces, nb_removed = remove_match_spaces(inner_text_spaces, match, nb_removed, keep_one)
            new_text = text[:inner_match.span()[0]] + inner_text_spaces + text[inner_match.span()[1]:]
    return new_text


def remove_spaces_after(text, char, keep_one=False):
    new_text = text
    for inner_match in re.finditer(">[^<]+", text):
        nb_removed = 0
        inner_text = inner_match.group()
        inner_text_spaces = inner_text.replace(char, char + " ")
        for match in re.finditer("".join(["\\", char, " *"]), inner_text_spaces):
            inner_text_spaces, nb_removed = remove_match_spaces(inner_text_spaces, match, nb_removed, keep_one)
            new_text = text[:inner_match.span()[0]] + inner_text_spaces + text[inner_match.span()[1]:]
    return new_text


def remove_match_spaces(text, match, nb_removed, keep_one=False):
    cleaned = match.group()
    if keep_one:
        count = len(re.findall(" ", cleaned)) - 1
        if not count == 0:
            cleaned = re.sub(" ", "", cleaned, count=count)
    else:
        cleaned = re.sub(" ", "", cleaned)
    if not match.group() == cleaned:
        text = text[:match.span()[0] - nb_removed] + cleaned + text[match.span()[1] - nb_removed:]
        nb_removed += len(match.group()) - len(cleaned)

    return text, nb_removed


def handle_special_spaces(text, ponct):
    text = "".join(["<remove>", text, "<remove>"])
    for char in ponct["space_after"]:
        text = remove_spaces_before(text, char)
        text = remove_spaces_after(text, char, True)

    for char in ponct["space_before"]:
        text = remove_spaces_before(text, char, True)
        text = remove_spaces_after(text, char)

    for char in ponct["space_before_and_after"]:
        text = remove_spaces_before(text, char, True)
        text = remove_spaces_after(text, char, True)

    for char in ponct["no_spaces"]:
        text = remove_spaces_before(text, char)
        text = remove_spaces_after(text, char)

    text = text.replace("<remove>", "")
    return text


def handle_redondant_spaces(text):
    nb_removed = 0
    for match in re.finditer("".join([space_regex(), "+"]), text):
        text, nb_removed = remove_match_spaces(text, match, nb_removed, True)

    text = re.sub("".join([r" ", balise_regex(), "*$"]), "", text)
    return text


def space_regex():
    return "".join(["(", balise_regex(), "* +(", balise_regex(), "*)*)"])


def balise_regex():
    return "(<[^>]*>)"


def beautifier(f_ret, ponct, contract):
    f_ret = new_contraction(f_ret, contract)
    f_ret = " ".join(handle_capitalize(copy.copy(ponct["capitalize"]), f_ret))
    f_ret = handle_special_spaces(f_ret, ponct)
    f_ret = handle_dots(f_ret)
    f_ret = handle_redondant_spaces(f_ret)
    for key, value in interpretable_char_reverse.items():
        f_ret = f_ret.replace("#" + key + "#", value)

    return f_ret


def debug_printer(f):
    @functools.wraps(f)
    def debug_printer_f(*args, **kwargs):
        f_ret = f(*args, **kwargs)
        arguments = list()
        for arg in args[1:]:
            if isinstance(arg, list):
                arguments.append([a for a in arg])
            elif isinstance(arg, html.HtmlElement):
                arguments.append(html.tostring(arg).decode("utf-8"))
            else:
                arguments.append(arg)

        args[0].logger.debug(
            "function {} called with param args{}, kwargs{}".format(
                f.__name__, arguments, kwargs
            )
        )
        if isinstance(f_ret, html.HtmlElement):
            args[0].logger.info(
                "function {} return : \n{}\n".format(
                    f.__name__, html.tostring(f_ret, encoding="utf-8").decode("utf-8")
                )
            )
        else:
            args[0].logger.info("function {} return : \n{}\n".format(f.__name__, f_ret))
        if args[0].active_all_printers:
            print(
                "fonction {}, arguments : {}\n{}".format(
                    f.__name__, args[1:], f_ret.text_content()
                )
            )
        return f_ret

    return debug_printer_f


def args_checker(f):
    @functools.wraps(f)
    def args_checker_f(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], list):
            e = Errors.ArgsNotUnpackedError
            args[0].logger.error("function {} return : {!s}".format(f.__name__, e))
            raise e
        return f(*args, **kwargs)

    return args_checker_f


def remove_technical_span(f):
    @functools.wraps(f)
    def remove_technical_span_f(*args, **kwargs):
        text = f(*args, **kwargs)
        for span in text.xpath("//span[@class='to_delete']"):
            span.drop_tag()
        return text

    return remove_technical_span_f
