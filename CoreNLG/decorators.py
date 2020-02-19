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


def contraction(splitters, current, contract, *text):

    if len(splitters) > current:
        splitted = list()
        for arg in text:
            for elem in arg.split(splitters[current]):
                splitted.append(elem)
                splitted.append(splitters[current])
            splitted.pop(-1)
        splitted = contraction(splitters, current + 1, contract, *splitted)
        return splitted
    else:
        splitted = list(text)
        new_sent = list()
        is_replaced = False
        for i in range(len(splitted)):
            if is_replaced:
                is_replaced = False
                continue
            try:
                w = splitted[i]
            except IndexError:
                break
            try:
                replacers = contract[w.lower()]
                for rep, comp_pattern in replacers.items():
                    if len(splitted) > i + 1:
                        w1 = splitted[i + 1]
                    else:
                        break
                    if w1 == " " and len(splitted) > i + 2:
                        w1 = splitted[i + 2]
                    else:
                        break
                    for e in comp_pattern:
                        try:
                            if isinstance(e, tuple):
                                comp_w1 = e[0]
                                replace = e[1]
                            else:
                                comp_w1 = e
                                replace = w1
                            if len(comp_w1) == 1 and w1[0].lower() == comp_w1:
                                is_replaced = True
                                if w[0].isupper():
                                    rep = rep[0].upper() + "".join(rep[1:])
                                new_sent.append(rep + replace[0] + "".join(w1[1:]))
                                splitted.pop(i)
                                break
                            elif w1.lower() == comp_w1:
                                is_replaced = True
                                if w[0].isupper():
                                    rep = rep[0].upper() + "".join(rep[1:])
                                new_sent.append(rep + replace)
                                splitted.pop(i)
                                break

                        except IndexError:
                            pass
                    if is_replaced:
                        break
            except KeyError:
                pass
            if not is_replaced or len(splitted) == i:
                new_sent.append(w)
        return "".join(new_sent)


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
    nb_removed = 0
    for match in re.finditer("".join([space_regex(), "+", "\\", char]), text):
        text, nb_removed = remove_match_spaces(text, match, nb_removed, keep_one)
    return text


def remove_spaces_after(text, char, keep_one=False):
    nb_removed = 0
    for match in re.finditer("".join(["\\", char, space_regex(), "+"]), text):
        text, nb_removed = remove_match_spaces(text, match, nb_removed, keep_one)
    return text


def remove_match_spaces(text, match, nb_removed, keep_one=False):
    cleaned = match.group()
    if keep_one:
        count = len(re.findall(" ", cleaned)) - 1
        if not count == 0:
            cleaned = re.sub(" ", "", cleaned, count=len(re.findall(" ", cleaned)) - 1)
    else:
        cleaned = re.sub(" ", "", cleaned)
    if not match.group() == cleaned:
        text = text[:match.span()[0] - nb_removed] + cleaned + text[match.span()[1] - nb_removed:]
        nb_removed += len(match.group()) - len(cleaned)

    return text, nb_removed


def handle_special_spaces(text, ponct):
    for char in ponct["space_after"]:
        text = text.replace(char, "".join([char, " "]))
        text = remove_spaces_before(text, char)
        text = remove_spaces_after(text, char, True)

    for char in ponct["space_before"]:
        text = text.replace(char, "".join([" ", char]))
        text = remove_spaces_before(text, char, True)
        text = remove_spaces_after(text, char)

    for char in ponct["space_before_and_after"]:
        text = text.replace(char, "".join([" ", char, " "]))
        text = remove_spaces_before(text, char, True)
        text = remove_spaces_after(text, char, True)

    for char in ponct["no_spaces"]:
        text = remove_spaces_before(text, char)
        text = remove_spaces_after(text, char)
    return text


def handle_redondant_spaces(text):
    nb_removed = 0
    for match in re.finditer("".join([space_regex(), "+"]), text):
        text, nb_removed = remove_match_spaces(text, match, nb_removed, True)

    text = re.sub("".join([r" ", balise_regex(), "*$"]), "", text)
    return text


def space_regex():
    return "".join(["( +(", balise_regex(), "*)*)"])


def balise_regex():
    return "(<[^>]*>)"


def beautifier(f_ret, ponct, contract):
    ignore_chars = [
        " ",
        ",",
        "'",
        "!",
        ";",
        ":",
        "/",
        '"',
        "?",
        "(",
        ")",
        ".",
        "<",
        ">",
    ]
    f_ret = contraction(
        ignore_chars, 0, contract, contraction(ignore_chars, 0, contract, f_ret)
    )
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
