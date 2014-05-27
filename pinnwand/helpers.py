#!/usr/bin/env python
from pygments.lexers import get_all_lexers

def _get_pygments_lexers(add_empty=True):
    r = []
    if add_empty:
        r.append(('', ''),)
    for lexer in get_all_lexers():
        r.append((lexer[1][0], lexer[0]),)
    return r

def list_languages():
    languages = _get_pygments_lexers()
    languages.sort(key=lambda x: x[1].lstrip(' _-.').lower())

    return languages
