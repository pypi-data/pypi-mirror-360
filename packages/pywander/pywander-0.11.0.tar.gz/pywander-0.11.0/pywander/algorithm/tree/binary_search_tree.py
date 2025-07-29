#!/usr/bin/env python
# -*-coding:utf-8-*-

from . import Tree


class BinarySearchTree(Tree):
    """
    binary search tree
    """

    def __str__(self):
        if self.parent is None:
            return '<BinarySearchTree: {0}>'.format(self.name)
        else:
            return '<BinarySearchTreeNode: {0}>'.format(self.name)

    def __repr__(self):
        if self.parent is None:
            return '<BinarySearchTree: {0}>'.format(self.name)
        else:
            return '<BinarySearchTreeNode: {0}>'.format(self.name)

    @property
    def left(self):
        if len(self.children) == 0:
            self.children = [None, None]
        elif len(self.children) == 1:
            self.children.append(None)

        return self.children[0]

    @left.setter
    def left(self, node):
        self.children[0] = node

    @property
    def right(self):
        if len(self.children) == 0:
            self.children = [None, None]
        elif len(self.children) == 1:
            self.children.append(None)

        return self.children[1]

    @right.setter
    def right(self, node):
        self.children[-1] = node

    def insert(self, name):
        if hash(name) < hash(self.name):
            if self.left is None:
                self.left = BinarySearchTree(name, parent=self)
            else:
                self.left.insert(name)
        elif hash(name) > hash(self.name):
            if self.right is None:
                self.right = BinarySearchTree(name, parent=self)
            else:
                self.right.insert(name)
        else:
            self.name = name

    def find(self, name):
        if hash(name) < hash(self.name):
            if self.left is None:
                return False
            else:
                return self.left.find(name)
        elif hash(name) > hash(self.name):
            if self.right is None:
                return False
            else:
                return self.right.find(name)
        else:
            return self


if __name__ == '__main__':
    tree = BinarySearchTree(8)

    tree.insert(3)
    tree.insert(10)
    tree.insert(1)
    tree.insert(6)
    tree.insert(14)
    tree.insert(4)
    tree.insert(7)
    tree.insert(13)

    assert tree.find(4)
    assert not tree.find(50)
