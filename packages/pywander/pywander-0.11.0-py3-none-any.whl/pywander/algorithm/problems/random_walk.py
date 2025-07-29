#!/usr/bin/env python
# -*-coding:utf-8-*-

import random
from math import sqrt


class Location(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        return Location(self.x + dx, self.y + dy)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def distance(self, other):
        ox, oy = other.x, other.y
        distance = sqrt((self.x - ox) ** 2 + (self.y - oy) ** 2)
        return distance

    def __str__(self):
        return f'<Location ({self.x}, {self.y})>'


class Drunk(object):
    def __init__(self, name=None):
        self.name = name

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return 'Anonymous'


class UsualDrunk(Drunk):
    def take_step(self):
        step_choices = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return random.choice(step_choices)


class Field(object):
    def __init__(self):
        self.drunks = {}

    def add_drunk(self, drunk, loc):
        if isinstance(loc, (tuple, list)):
            assert len(loc) == 2
            loc = Location(loc[0], loc[1])

        if drunk in self.drunks:
            raise ValueError('Duplicate drunk')
        else:
            self.drunks[drunk] = loc

    def move_drunk(self, drunk):
        if drunk not in self.drunks:
            raise ValueError('Drunk not in field')

        dx, dy = drunk.take_step()
        current_loc = self.drunks[drunk]
        self.drunks[drunk] = current_loc.move(dx, dy)

    def get_loc(self, drunk):
        if drunk not in self.drunks:
            raise ValueError('Drunk not in field')

        return self.drunks[drunk]


def walk(f, d, num_steps):
    start = f.get_loc(d)
    for s in range(num_steps):
        f.move_drunk(d)

    return start.distance(f.get_loc(d))


def bulk_walk(num_steps, num_bulk, dClass):
    """
    :param num_steps: 随机行走了多少步
    :param num_bulk: 一批次进行了多少次实验
    :param dClass: 醉汉类型
    :return: distances 一批次里面每次开图的总共行走距离列表
    """
    drunk = dClass()
    origin = Location(0, 0)
    distances = []
    for i in range(num_bulk):
        f = Field()
        f.add_drunk(drunk, origin)
        distances.append(round(walk(f, drunk, num_steps), 1))
    return distances


def drunk_test(num_steps_batch, num_bulk, dClass):
    """

    :param num_steps_batch: 随机行走多少步填入批次
    :param num_bulk: 一批次进行了多少次实验
    :param dClass: 醉汉类型
    :return:
    """
    mean_distance_list = []
    for num_steps in num_steps_batch:
        distances = bulk_walk(num_steps, num_bulk, dClass)
        print(f'{dClass.__name__} random walk of {num_steps} steps')
        mean_distance = round(sum(distances) / len(distances), 4)
        mean_distance_list.append(mean_distance)
        print(f'Mean = {mean_distance}')
        print(f'Max = {max(distances)} Min = {min(distances)}')

    return mean_distance_list


if __name__ == '__main__':
    num_steps_batch = list(range(100, 3000, 100))
    data = drunk_test(num_steps_batch, 100, UsualDrunk)
