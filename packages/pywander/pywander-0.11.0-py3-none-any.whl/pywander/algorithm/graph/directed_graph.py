#!/usr/bin/env python
# -*-coding:utf-8-*-

from pywander.algorithm.graph.graph import Graph
from pywander.algorithm.graph.exceptions import AdditionError


class DirectedGraph(Graph):
    """
    graph_data structure as:
     {
         'a': ['b','z']
     }
     """
    DIRECTED = True

    def __init__(self, graph_data=None):
        """
        Initialize a graph.
        """
        self.graph_data = graph_data if graph_data is not None else {}

    def nodes(self):
        """
        Return nodes
        """
        return self.graph_data.keys()

    def neighbors(self, node) -> list:
        """
        Return all nodes that are incident to the given node.
        """
        return self.graph_data[node]

    def _generate_edges(self):
        """
        represent edge as (a,b)
        """
        edges = []
        for node in self.nodes():
            for neighbor in self.neighbors(node):
                if (node, neighbor) not in edges:
                    edges.append((node, neighbor))
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

    def has_edge(self, edge) -> bool:
        """
        Return whether an edge exists.
        """
        u, v = edge
        return (u, v) in self.edges()

    def add_node(self, node):
        """
        Add given node to the graph.
        """
        if self.has_node(node):
            raise AdditionError("Node {0} already in digraph".format(node))

        self.graph_data[node] = []

    def add_edge(self, edge):
        """
        Add an directed edge to the graph connecting two nodes.
        """
        u, v = edge
        if self.has_edge(edge):
            raise AdditionError("Edge (%s, %s) already in digraph" % (u, v))

        for n in [u, v]:
            if n not in self.graph_data:
                self.add_node(n)

        self.graph_data[u].append(v)

    def del_node(self, node):
        """
        Remove a node from the graph.
        """
        for edge in self.edges():
            a, b = edge
            if b == node:
                self.del_edge((a, node))

        # Remove this node from the neighbors and incidents tables
        del (self.graph_data[node])

    def del_edge(self, edge):
        """
        Remove an directed edge from the graph.
        """
        u, v = edge
        if v in self.graph_data[u]:
            self.graph_data[u].remove(v)

    def out_degree(self, node):
        """
        return the target node's out degree
        """
        count = 0
        if node in self.graph_data:
            count = len(self.graph_data[node])

        return count

    def in_degree(self, node):
        """
        return the target node's in degree
        """
        count = 0
        for k, v in self.graph_data.items():
            if node in v:
                count += 1

        return count

    def __ne__(self, other):
        """
        Return whether this graph is not equal to another one.
        """
        return not (self == other)
