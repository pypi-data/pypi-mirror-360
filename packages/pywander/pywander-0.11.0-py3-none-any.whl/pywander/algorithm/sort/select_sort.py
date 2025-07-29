#!/usr/bin/env python
# -*-coding:utf-8-*-


"""
select_sort nearly equal with the select_sort2, but the select_sort2 has
a more understandable writing style.

"""

def select_sort(seq):
    seq2 = seq.copy()
    for i in range(0, len(seq2)):
        minimum = i
        for j in range(i + 1, len(seq2)):
            if seq2[j] < seq2[minimum]:
                minimum = j
        seq2[i], seq2[minimum] = seq2[minimum], seq2[i]

    return seq2


def select_sort2(seq):
    """
    :param seq:
    :return:
    """

    def find_smallest_index(seq):
        smallest = seq[0]
        smallest_index = 0
        for i in range(1, len(seq)):
            target = seq[i]
            if target < smallest:
                smallest = target
                smallest_index = i
        return smallest_index

    res = []
    seq_copy = seq.copy()

    for i in range(0, len(seq)):
        smallest_index = find_smallest_index(seq_copy)
        res.append(seq_copy.pop(smallest_index))

    return res
