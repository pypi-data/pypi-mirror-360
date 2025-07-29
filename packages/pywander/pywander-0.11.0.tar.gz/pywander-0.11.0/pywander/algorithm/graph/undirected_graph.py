#!/usr/bin/env python
# -*-coding:utf-8-*-

from copy import copy
from . import Graph
from .exceptions import AdditionError


class UndirectedGraph(Graph):
    """
    graph_data structure as:
    {
        'a': {'b','z'}
    }
    """
    DIRECTED = False

    def __init__(self, graph_data=None):
        """
        Initialize a graph.
        """
        self.graph_data = graph_data if graph_data is not None else {}

    def nodes(self):
        """
        Return node list.
        """
        return self.graph_data.keys()

    def neighbors(self, node) -> list:
        """
        Return all nodes that are directly accessible from given node.
        """
        return list(self.graph_data[node])

    def _generate_edges(self):
        """
        represent edge as {a,b}
        """
        edges = []
        for node in self.nodes():
            for neighbour in self.neighbors(node):
                if {neighbour, node} not in edges:
                    edges.append({node, neighbour})
        return edges

    def edges(self):
        """
        Return all edges in the graph.
        """
        return self._generate_edges()

    def has_node(self, node) -> bool:
        """
        Return whether the requested node exists.
        """
        return node in self.graph_data

    def _read_edge(self, edge):
        data = copy(edge)

        if len(data) == 1:
            u = v = data.pop()
        elif len(data) == 2:
            u, v = data
        else:
            raise Exception("wrong edge format")

        return u, v

    def has_edge(self, edge) -> bool:
        """
        Return whether an edge exists.
        """
        u, v = self._read_edge(edge)

        return {u, v} in self.edges()

    def add_node(self, node):
        """
        Add given node to the graph.
        """
        if self.has_node(node):
            raise AdditionError("Node %s already in graph" % node)

        self.graph_data[node] = set()

    def add_edge(self, edge):
        """
        Add an edge to the graph connecting two nodes.
        """
        u, v = self._read_edge(edge)

        if self.has_edge(edge):
            raise AdditionError("Edge ({0}, {1}) already in graph".format(u, v))

        for n in [u, v]:
            if n not in self.graph_data:
                self.add_node(n)

        self.graph_data[u].add(v)
        if u != v:
            self.graph_data[v].add(u)

    def del_node(self, node):
        """
        Remove a node from the graph.
        """
        for each in list(self.neighbors(node)):
            if each != node:
                self.del_edge((each, node))
        del (self.graph_data[node])

    def del_edge(self, edge):
        """
        Remove an edge from the graph.
        """
        u, v = self._read_edge(edge)

        self.graph_data[u].remove(v)
        if u != v:
            self.graph_data[v].remove(u)

    def __ne__(self, other):
        """
        Return whether this graph is not equal to another one.
        """
        return not (self == other)
