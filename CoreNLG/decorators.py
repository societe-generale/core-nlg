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
            match = re.search("".join([r"^", "( |\n|<[^>]*>)*[a-z]"]), new_string)
            if match is not None:
                matchs.append(match)
        matchs += re.finditer("".join(["(\\" + "|\\".join(splitters), ")( |\n|<[^>]*>)*[a-z]"]), new_string)
        for match in matchs:
            new_string = new_string[:match.span()[1] - 1] + new_string[match.span()[1] - 1].upper() + new_string[match.span()[1]:]
        capitalized_text.append(new_string)
    return capitalized_text


def new_contraction(text, contracts):
    re_contract = False
    for contract in contracts:
        candidats = list()
        search_1 = -1
        for search, replace in contract.items():
            if search_1 == -1:
                search_1 = len(re.findall("".join([search[0], "\\W"]), text))
                if search_1 == 0:
                    break
            if len(re.findall("".join(["(", search[0], ")\\W+(", search[1], ")"]), text)) == 0:
                continue
            for match in re.finditer("".join(["((\\W|^))(", search[0], ")[^a-zA-Z0-9<>]+(", search[1], ")"]), text):
                replacer = list()
                for g in match.groups():
                    replacer.append(g if g is not None else "")
                replacer[2] = replace[0]
                replacer[-1] = replace[1].capitalize() if replacer[-1][0].isupper() else replace[1]
                replacer.pop(0)
                candidats.append((match.group(), replacer))
        if len(candidats) > 0:
            candidats.sort(key=lambda t: len(t[0]), reverse=True)
            text = text.replace(candidats[0][0], "".join(candidats[0][1]))
            re_contract = True
    if re_contract:
        text = new_contraction(text, contracts)
    return text


def handle_dots(text):
    matchs = re.finditer(r"(\.((<[^>]*>)|\W)*){2,}", text)
    nb_removed = 0
    for match in matchs:
        nb_dots = len(re.findall(r"\.", match.group()))
        cleaned_dots = match.group()
        cleaned_dots = re.sub(" \\.", ".", cleaned_dots)
        if nb_dots == 2:
            cleaned_dots = re.sub("\\.", "", cleaned_dots, count=1)
            text = "".join([text[:match.span()[0] - nb_removed], cleaned_dots, text[match.span()[1] - nb_removed:]])
        elif nb_dots >= 3:
            if nb_dots > 3:
                cleaned_dots = re.sub("\\.", "", cleaned_dots, count=nb_dots - 3)
            text = "".join([text[:match.span()[0] - nb_removed], cleaned_dots, text[match.span()[1] - nb_removed:]])
        nb_removed += len(match.group()) - len(cleaned_dots)
    return text


def handle_redundant_punctuations(text, punctuations):
    for v in punctuations.values():
        for char in v:
            if char == ".":
                continue
            char = "".join(["\\", char])
            matchs = re.finditer("".join(["(", char, "((<[^>]*>)|\\W)*){2,}"]), text)
            nb_removed = 0
            for match in matchs:
                cleaned_dots = match.group()
                nb_dots = len(re.findall(char, cleaned_dots))
                cleaned_dots = re.sub(char, "", cleaned_dots, count=nb_dots - 1)
                text = "".join([text[:match.span()[0] - nb_removed], cleaned_dots, text[match.span()[1] - nb_removed:]])
                nb_removed += len(match.group()) - len(cleaned_dots)
    return text


def remove_spaces_before(text, char, keep_one=False):
    nb_removed = 0
    for inner_match in re.finditer(">[^<]+", text):

        inner_text = inner_match.group()
        inner_text_spaces = inner_text.replace(char, " " + char)

        sub = "".join([" ", char]) if keep_one else char
        inner_text_sub = re.sub("".join([" *\\", char]), sub, inner_text_spaces)
        if inner_text_sub != inner_text_spaces or inner_text_sub != inner_text:
            text = text[:inner_match.span()[0] - nb_removed] + inner_text_sub + text[inner_match.span()[1] - nb_removed:]
            nb_removed += len(inner_text) - len(inner_text_spaces)
            nb_removed += len(inner_text_spaces) - len(inner_text_sub)
    return text


def remove_spaces_after(text, char, keep_one=False):
    nb_removed = 0
    for inner_match in re.finditer(">[^<]+", text):
        inner_text = inner_match.group()
        inner_text_spaces = inner_text.replace(char, char + " ")
        sub = "".join([char, " "]) if keep_one else char
        inner_text_sub = re.sub("".join(["\\", char, " *"]), sub, inner_text_spaces)
        if inner_text_sub != inner_text_spaces or inner_text_sub != inner_text:
            text = text[:inner_match.span()[0] - nb_removed] + inner_text_sub + text[inner_match.span()[1] - nb_removed:]
            nb_removed += len(inner_text) - len(inner_text_spaces)
            nb_removed += len(inner_text_spaces) - len(inner_text_sub)
    return text


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
    for match in re.finditer("".join([" +"]), text):
        text, nb_removed = remove_match_spaces(text, match, nb_removed, True)

    text = re.sub("".join([r" ", balise_regex(), "*$"]), "", text)
    return text


def balise_regex():
    return "(<[^>]*>( *\n*)*)"


def beautifier(f_ret, ponct, contract):
    f_ret = new_contraction(f_ret, contract)
    f_ret = " ".join(handle_capitalize(copy.copy(ponct["capitalize"]), f_ret))
    f_ret = handle_special_spaces(f_ret, ponct)
    f_ret = handle_dots(f_ret)
    f_ret = handle_redundant_punctuations(f_ret, ponct)
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
