
def hanoi(disks, source, helper, destination):
    """
    Recursive function for Tower of Hanoi
    hanoi(3, 'A', 'B', 'C')
    """
    # Base Condition
    if (disks == 1):
        print('Disk {} moves from tower {} to tower {}.'.format(disks, source, destination))
        return

    # Recursive calls in which function calls itself
    hanoi(disks - 1, source, destination, helper)
    print('Disk {} moves from tower {} to tower {}.'.format(disks, source, destination))

    hanoi(disks - 1, helper, source, destination)


