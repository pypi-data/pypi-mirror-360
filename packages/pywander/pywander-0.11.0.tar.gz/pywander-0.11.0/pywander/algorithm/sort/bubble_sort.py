def bubble_sort(lst):
    """
        bubble sort

    >>> lst = [5, 4, 55, 6, 9, 1]
    >>> bubble_sort(lst)
    [1, 4, 5, 6, 9, 55]

    """
    new_lst = lst.copy()

    while True:
        swapped = False

        for i in range(len(new_lst) - 1):
            if new_lst[i] > new_lst[i + 1]:
                new_lst[i], new_lst[i + 1] = new_lst[i + 1], new_lst[i]
                swapped = True

        if not swapped:
            return new_lst


