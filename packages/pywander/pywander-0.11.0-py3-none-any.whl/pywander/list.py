#!/usr/bin/env python
# -*-coding:utf-8-*-

from itertools import product, permutations, combinations, \
    combinations_with_replacement


def del_list(lst: list, indexs):
    """
    del list base a index list

>>> del_list([0,1,2,3,4,5],[2,3])
[0, 1, 4, 5]
>>> lst = list(range(6))
>>> lst
[0, 1, 2, 3, 4, 5]
>>> del_list(lst,[2,3])
[0, 1, 4, 5]
>>> lst
[0, 1, 4, 5]
>>> del_list(lst,[0,2])
[1, 5]
>>> lst
[1, 5]

    """
    count = 0
    for index in sorted(indexs):
        index = index - count
        del lst[index]
        count += 1
    return lst


def group_list(lst: list, n=1):
    """
    group a list, in some case, it is maybe useful.

>>> list(group_list(list(range(10)),0))
Traceback (most recent call last):
AssertionError
>>> list(group_list(list(range(10)),1))
[[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]]
>>> list(group_list(list(range(10)),2))
[[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
>>> list(group_list(list(range(10)),3))
[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
>>> list(group_list(list(range(10)),4))
[[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

    """
    assert n > 0
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def combine_odd_even(lst):
    """
    odd and even element do the add operation
    """
    res = []
    for item in group_list(lst, 2):
        if len(item) > 1:
            a, b = item
            res.append(a + b)
        else:
            a = item[0]
            res.append(a)
    return res


def double_iter(lst: list, mode='combinations'):
    """
    if the list is [A, B, C,D ]
    mode default value is combinations:
    which means no self-repeat and elements compare with no order.
    default mode will yield
    (A,B) (A,C) (A,D) (B,C) ...

    if set mode = product will yield
    which is equal two for-loop clause
    (A,A) (A,B) (A,C) (A,D) (B,A) (B,B) ...

    if set mode = permutations, will yield
    (A,B) (A,C) (A,D) (B,A) (B,C) (B,D) ...
    which means no self-repeat and elements compare with order.

    if set mode = combinations_with_replacement, will yield
    (A, A) (A, B) (A, C) (A, D) (B, B) (B, C) (B, D) ...
    which means with self-repeat and elements compare with no order.
    """

    if mode == 'combinations':
        return combinations(lst, 2)
    elif mode == 'product':
        return product(lst, repeat=2)
    elif mode == 'permutations':
        return permutations(lst, 2)
    elif mode == 'combinations_with_replacement':
        return combinations_with_replacement(lst, 2)
