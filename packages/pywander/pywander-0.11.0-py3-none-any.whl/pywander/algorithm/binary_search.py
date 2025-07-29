#!/usr/bin/env python
# -*-coding:utf-8-*-


import logging
from bisect import insort_left, bisect_left

logger = logging.getLogger(__name__)


def binary_search_func(seq, target, func=lambda x: x, round_n=4, approx=True):
    """
    use binary search to solve f(x) = target problem, if the function is a
    monotonic function.

    seq  list or tuple
    target found target in which case is the f(x) = target
    func the monotonic function
    round_n accurate to how many decimal point
    approx the approx mode
    if approx=True found target or some nearly target, return it's index
    if approx=False  found target index otherwise return -1
    """
    low = 0
    high = len(seq) - 1
    count = 0

    while low < high:
        count += 1
        mid = (high + low) // 2

        guess = func(seq[mid])

        if approx:
            target = round(target, round_n)
            guess = round(guess, round_n)

        if guess < target:  # equal target the target also placed in big region.
            low = mid + 1
        else:  # target in low region
            high = mid

    logger.info('binary_search_func run {0} times'.format(count))
    if approx:
        return low
    else:
        return low if (low != len(seq) and seq[low] == target) else -1


def binary_search(seq, target):
    """
    use the bisect_left.
    """
    pos = bisect_left(seq, target)
    # pos == len(seq) means the target is bigger than all the elements of seq
    # other pos value is a valid index in seq
    # So if x already appears in the list, a.insert(x) will
    # insert just before the leftmost x already there.
    return pos if (pos != len(seq) and seq[pos] == target) else -1


def binary_insert(seq, target):
    """
    use the insort_left
    """
    insort_left(seq, target)
    return seq
