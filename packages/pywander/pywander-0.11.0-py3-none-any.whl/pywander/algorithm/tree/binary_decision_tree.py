#!/usr/bin/env python
# -*-coding:utf-8-*-





class BinaryDecisionTree(object):
    """
    二叉决策树

    决策函数 data
    decisions = [('a',True), ('b',False)] 决定了决策树中节点在决策树中的位置

    """

    def __init__(self, data=None, decisions=None, parent=None):
        self.left = None
        self.right = None

        self.data = data

        if decisions is None:
            decisions = []

        self.decisions = decisions

        self.parent = parent

    def __repr__(self):
        return '<BinaryDecisionTree {0} {1}>'.format(self.decisions, self.data)

    def append(self, child_data, new_decision):
        """
        本节点附加
        :param child_data:
        :param new_decision:
        :return:
        """
        bool_key, bool_value = new_decision
        if bool_value:
            decisions = self.decisions + [new_decision]
            self.left = BinaryDecisionTree(child_data, decisions=decisions, parent=self)
            return self.left
        else:
            decisions = self.decisions + [new_decision]
            self.right = BinaryDecisionTree(child_data, decisions=decisions, parent=self)
            return self.right

    def insert(self, child_data, decisions, auto_create=False):
        """
        插在某个节点上
        :param bool_key:
        :param child_data:
        :return:
        """

        if len(decisions) == 1:
            target = self.find()
            new_decision = decisions
        else:
            target = self.find(decisions[:-1], auto_create=auto_create)
            new_decision = decisions[-1]

        new_node = target.append(child_data, new_decision=new_decision)
        return new_node

    def find(self, decisions=None, auto_create=False):
        if decisions is None:
            assert self.parent is None
            return self

        res = None

        for target in self.introspection():
            if target.decisions == decisions:
                res = target
                return res

        if res is None:
            if auto_create:
                for i in range(1, len(decisions) + 1):
                    decisions_small = decisions[:i]
                    if not self.find(decisions_small):
                        self.insert(child_data=None, decisions=decisions_small)
            else:
                return None

    def set_data(self, data):
        self.data = data

    def introspection(self):
        stack = []
        node = self
        while stack or node:
            if node:
                stack.append(node)
                node = node.left
            else:
                node = stack.pop()
                yield node
                node = node.right
        return stack

    def children_count(self):
        """Return the number of children

        @returns number of children: 0, 1, 2
        """
        cnt = 0
        if self.left:
            cnt += 1
        if self.right:
            cnt += 1
        return cnt


if __name__ == '__main__':
    data_0 = {'pre': [], 'post': ['a', 'b', 'c', 'd']}
    data_1 = {'pre': ['a'], 'post': ['b', 'c', 'd'], 'decisions': [('a', True)]}
    data_2 = {'pre': [], 'post': ['b', 'c', 'd'], 'decisions': [('a', False)]}
    tree = BinaryDecisionTree(data_0)
    tree.append(data_1, new_decision=('a', True))
    tree.append(data_2, new_decision=('a', False))
