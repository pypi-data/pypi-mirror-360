#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging
from .exceptions import InsertError

logger = logging.getLogger(__name__)


def _path_to(node):
    assert isinstance(node, Tree)

    path = []
    target = node
    while True:
        path.append(target)

        if target.parent is None:
            break
        else:
            target = target.parent
    return path[::-1]


class Tree(object):
    """
    the brother nodes can not have the same name.
    """

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

    def __iter__(self):
        """
        iter all nodes, dfs style.
        """
        if self.name is not None:
            yield self

            for child in self.children:
                for i in child:
                    yield i

    def __str__(self):
        if self.parent is None:
            return '<Tree: {0}>'.format(self.name)
        else:
            return '<TreeNode: {0}>'.format(self.name)

    def __repr__(self):
        if self.parent is None:
            return '<Tree: {0}>'.format(self.name)
        else:
            return '<TreeNode: {0}>'.format(self.name)

    def has_node(self, node):
        """
        check whether this tree has this node.
        only check the node's name.
        """
        if isinstance(node, Tree):
            name = node.name
        elif isinstance(node, str):
            name = node
        else:
            raise TypeError("node wrong type")

        for target in self:
            if target.name == name:
                return True

        return False

    def has_child(self, node):
        """
        check whether this node has this child node.
        only check the node's name
        """
        if isinstance(node, Tree):
            name = node.name
        elif isinstance(node, str):
            name = node
        else:
            raise TypeError("node wrong type")

        for child in self.children:
            if child.name == name:
                return True

        return False

    def insert_child(self, parent_name, child_name):
        """
        insert a child
        """
        target = self[parent_name]

        if target.has_child(child_name):
            raise InsertError("child name exists")
        else:
            target.children.append(Tree(child_name, parent=target))

    def remove_child(self, child_name):
        target = self[child_name]
        parent = target.parent
        parent.children.remove(target)

    def __getitem__(self, name):
        """
        get target node only return first found one
        """
        for target in self:
            if target.name == name:
                return target
        raise KeyError

    def get_nodes(self, name):
        """
        get all target
        """
        for target in self:
            if target.name == name:
                yield target

    def to_json(self):
        return {self.name: [i.to_json() for i in self.children]}

    def to_flatten_list(self):
        """iter tree with dfs style"""
        return [i.name for i in self]

    @property
    def level(self):
        level = 1
        target = self

        while target.parent is not None:
            level += 1
            target = target.parent

        return level

    def shortest_path_to(self, node):
        """
        the shortest path to the target node
        """
        min_level = None
        min_path = None

        for target in self.get_nodes(node):
            target_level = target.level

            if min_level is None:
                min_level = target_level
                min_path = _path_to(target)

            if target_level < min_level:
                min_path = _path_to(target)

        return min_path


if __name__ == "__main__":
    tree = Tree("a")
    tree.insert_child("a", "b")
    tree.insert_child("a", "c")
    tree.insert_child("b", "d")
    tree.insert_child("b", "e")
    tree.insert_child("b", "f")
    tree.insert_child("c", "g")
    tree.insert_child("c", "h")
    tree.insert_child("d", "i")
    tree.insert_child("e", "j")

    print(tree)

    c = tree['c']

    print(c.parent)
    print(c.children)

    import json

    print(json.dumps(tree.to_json(), indent=2))
