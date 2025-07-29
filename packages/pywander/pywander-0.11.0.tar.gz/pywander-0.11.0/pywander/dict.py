#!/usr/bin/env python
# -*-coding:utf-8-*-


from functools import reduce

from pywander.compat import ispy2, ispy3


def _gen_dict_strset(d):
    s = set()
    for k, v in d.items():
        item = str(k) + ':' + str(v)
        s.add(item)
    return s


def compare_dict_include(d, include=None):
    """
    compare two dict object include or contained relationship

    return True : d totally contain the second dict

    >>> compare_dict_include({'a':1},{})
    True
    >>> compare_dict_include({'a':1},{'a':2})
    False
    >>> compare_dict_include({'a':1},{'a':1})
    True
    >>> compare_dict_include({'a':1,'b':2},{'a':1})
    True
    >>> compare_dict_include({'a':1,'b':2},{'b':2})
    True
    """
    include = include if include is not None else {}

    if include == {}:  # always True
        return True

    ds_set = _gen_dict_strset(d)
    includes_set = _gen_dict_strset(include)
    if includes_set.issubset(ds_set):
        return True
    else:
        return False


def check_dict_has(d, has=None):
    """
    does the dict object has some keys

    >>> check_dict_has({'a':1,'b':2},[])
    True
    >>> check_dict_has({'a':1,'b':2},['a'])
    True
    >>> check_dict_has({'a':1,'b':2},['a','c'])
    False
    >>> check_dict_has({'a':1,'b':2},['a','b'])
    True

    """
    has = has if has is not None else []

    if has == []:  # always True
        return True

    if set(has).issubset(set(d.keys())):
        return True
    else:
        return False


def merge_dict(*args):
    """
    merge multi-dict, if there is a duplicate key, the value is decide by the last one.

    ref : http://stackoverflow.com/questions/38987/\
    how-can-i-merge-two-python-dictionaries-in-a-single-expression

    >>> merge_dict({'a': 1, 'b': 2}, {'b': 10, 'c': 11})
    {'a': 1, 'b': 10, 'c': 11}

    """

    def add(x, y):
        return x + y

    if ispy2:
        res = dict(reduce(add, [d.items() for d in args]))
        return res
    elif ispy3:
        res = dict(reduce(add, [list(d.items()) for d in args]))
        return res


def sorted_dict_by_value(d, **kwargs):
    """
    sorted dict by it's value

    >>> sorted_dict_by_value({'andy':5,'Andy':1,'black':9,'Black':55})
    [('Andy', 1), ('andy', 5), ('black', 9), ('Black', 55)]

    """
    return sorted(d.items(), key=lambda i: i[1], **kwargs)
