#!/usr/bin/env python
# -*-coding:utf-8-*-

"""
graph models

- Graph
- UndirectedGraph
- DirectedGraph
- WeightedDirectedGraph
"""

from collections import deque
from abc import abstractmethod
from abc import ABC

from pywander.algorithm.tree import Tree


class Graph(ABC):
    """
    general graph class
    """
    DIRECTED = None

    @abstractmethod
    def nodes(self):
        raise NotImplementedError("Not Implement nodes methods")

    @abstractmethod
    def neighbors(self, node):
        raise NotImplementedError("Not Implement neighbors methods")

    @abstractmethod
    def edges(self):
        raise NotImplementedError("Not Implement edges methods")

    @abstractmethod
    def has_node(self, node):
        raise NotImplementedError("Not Implement has_node methods")

    @abstractmethod
    def has_edge(self, edge):
        raise NotImplementedError("Not Implement has_edge methods")

    @abstractmethod
    def add_node(self, node):
        raise NotImplementedError("Not Implement add_node methods")

    @abstractmethod
    def add_edge(self, edge):
        raise NotImplementedError("Not Implement add_edge methods")

    def __str__(self):
        str_nodes = repr(self.nodes())
        str_edges = repr(self.edges())
        return "{0} {1}".format(str_nodes, str_edges)

    def __repr__(self):
        return "<{0}.{1} {2}>".format(self.__class__.__module__,
                                      self.__class__.__name__, str(self))

    def __iter__(self):
        """
        Return a iterator passing through all nodes in the graph.
        """
        for n in self.nodes():
            yield n

    def __len__(self):
        """
        Return the order of self when requested by len().
        """
        return self.order()

    def __getitem__(self, node):
        """
        Return a iterator passing through all neighbors of the given node.
        """
        for n in self.neighbors(node):
            yield n

    def order(self):
        """
        Return the order of self, this is defined as the number of nodes in the graph.
        """
        return len(self.nodes())

    def add_nodes(self, nodelist):
        """
        Add given nodes to the graph.
        """
        for each in nodelist:
            self.add_node(each)

    def add_spanning_tree(self, st):
        """
        Add a spanning tree to the graph.
        """
        self.add_nodes(list(st.keys()))

        for each in st:
            if st[each] is not None:
                self.add_edge((st[each], each))

    def complete(self):
        """
        Make the graph a complete graph.
        """
        for each in self.nodes():
            for other in self.nodes():
                if each != other and not self.has_edge((each, other)):
                    self.add_edge((each, other))

    def __eq__(self, other):
        """
        Return whether this graph is equal to another one.
        """

        def nodes_eq():
            for each in self:
                if not other.has_node(each):
                    return False
            for each in other:
                if not self.has_node(each):
                    return False
            return True

        def edges_eq():
            for edge in self.edges():
                if not other.has_edge(edge):
                    return False
            for edge in other.edges():
                if not self.has_edge(edge):
                    return False
            return True

        try:
            return nodes_eq() and edges_eq()
        except AttributeError:
            return False

    def bfs_search(self, start):
        """
        Breadth-first search.
        """
        def bfs():
            """
            Breadth-first search sub-function.
            """
            while queue:
                node = queue.popleft()

                if node not in visited:
                    for other in self.neighbors(node):
                        bfs_tree.insert_child(node, other)
                        queue.append(other)

                    visited.append(node)

        queue = deque()  # Visiting queue
        visited = []
        bfs_tree = Tree(start)
        queue.append(start)

        bfs()
        return bfs_tree

    def dfs_search(self, start):
        """
        Depth-first search.
        """
        def dfs(node):
            """
            Depth-first search sub-function.
            """
            visited.append(node)

            for other in self.neighbors(node):
                if other not in visited:
                    dfs_tree.insert_child(node, other)
                    dfs(other)

        visited = []
        dfs_tree = Tree(start)
        dfs(start)

        return dfs_tree

    def bfs_shortest_path_search(self, start, end):
        def bfs():
            """
            Breadth-first search sub-function.
            """
            while queue:
                node = queue.popleft()

                if node not in visited:
                    for other in self.neighbors(node):
                        if other == end:
                            bfs_tree.insert_child(node, other)
                            break
                        else:
                            bfs_tree.insert_child(node, other)
                            queue.append(other)

                    visited.append(node)

        queue = deque()  # Visiting queue
        visited = []
        bfs_tree = Tree(start)
        queue.append(start)

        bfs()
        return bfs_tree

    def dfs_shortest_path_search(self, start, end):
        def dfs(node):
            """
            Depth-first search sub-function.
            """
            for other in self.neighbors(node):
                if other == end:
                    dfs_tree.insert_child(node, other)
                    break
                else:
                    dfs_tree.insert_child(node, other)
                    dfs(other)

        dfs_tree = Tree(start)
        dfs(start)

        return dfs_tree

    def bfs_shortest_path(self, start, end):
        bfs_tree = self.bfs_shortest_path_search(start, end)
        min_path = bfs_tree.shortest_path_to(end)
        return [i.name for i in min_path]

    def dfs_shortest_path(self, start, end):
        dfs_tree = self.dfs_shortest_path_search(start, end)
        min_path = dfs_tree.shortest_path_to(end)
        return [i.name for i in min_path]
