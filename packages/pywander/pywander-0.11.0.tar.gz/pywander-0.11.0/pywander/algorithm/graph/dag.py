#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging
from copy import deepcopy
from collections import deque

from .exceptions import NotAcyclicError
from .directed_graph import DirectedGraph

logger = logging.getLogger(__name__)


class DirectedAcyclicGraph(DirectedGraph):
    def add_edge(self, edge):
        """
        add acyclic judgement.
        """
        super().add_edge(edge)

        if not self.sort():
            self.remove_edge(edge)
            raise NotAcyclicError

    def remove_edge(self, edge):
        """
        remove edge start -> end
        """
        start, end = edge
        super(DirectedAcyclicGraph, self).del_edge((start, end))

        # clear data
        if self.in_degree(start) == 0 and self.out_degree(start) == 0:
            if start in self.graph_data:
                del self.graph_data[start]

        if self.in_degree(end) == 0 and self.out_degree(end) == 0:
            if end in self.graph_data:
                del self.graph_data[end]

    def sort(self):
        """
        L ← Empty list that will contain the sorted elements
        S ← Set of all nodes with no incoming edge
        while S is non-empty do
            remove a node n from S
            add n to tail of L
            for each node m with an edge e from n to m do
                remove edge e from the graph
                if m has no other incoming edges then
                    insert m into S
        if graph has edges then
            return error (graph has at least one cycle)
        else
            return L (a topologically sorted order)
        """
        target = deepcopy(self)
        top_order = []

        queue = deque()
        for k in target.nodes():
            if target.in_degree(k) == 0:
                queue.append(k)
                logger.debug('queue append {0}'.format(k))

        while queue:
            n = queue.pop()
            top_order.append(n)

            for m in self.neighbors(n):
                target.remove_edge((n, m))
                logger.debug('remove n->m {0} {1}'.format(n, m))
                if target.in_degree(m) == 0:
                    logger.debug('append {0}'.format(m))
                    queue.append(m)

        if len(top_order) != len(self.nodes()):
            return False
        else:
            return top_order
