#!/usr/bin/env python
# -*-coding:utf-8-*-

from functools import reduce


def build_compose_function(*funcs):
    """
    combine a sequence functions to a compose function
    """
    return reduce(lambda f, g: lambda *args, **kwargs: g(f(*args, **kwargs)), funcs)


def build_stream_function(*funcs):
    """
    combine a sequence funtion to a compose function, and for the sake of simplicity, 
    limited the input parameter to a dict object.
    """

    return reduce(lambda f, g: lambda d: g(f(d)), funcs)


def flatten(inlst):
    """
    make multiple layer list or tuple to one dimension list

        >>> flatten((1,2,(3,4),((5,6))))
        [1, 2, 3, 4, 5, 6]
        >>> flatten([[1,2,3],[[4,5],[6]]])
        [1, 2, 3, 4, 5, 6]

    """
    lst = []
    for x in inlst:
        if not isinstance(x, (list, tuple)):
            lst.append(x)
        else:
            lst += flatten(x)
    return lst


def sumall(*args):
    """sum all numbers, support multiple layer structure.
    
    >>> sumall(1,1,2,3,[1,2,3])
    13
    >>> sumall(1,1,2,3,[1,2,3],(4,5,6),[[5,5],[6]])
    44
    >>>
    """
    args = flatten(args)
    return sum(args)

def default_func(n):
    print(n)

def mathematical_induction(n, func=default_func):
    if n==1:
        return default_func(1)
    else:
        return mathematical_induction(n-1)

