#!/usr/bin/env python
# -*-coding:utf-8-*-

from . import DirectedAcyclicGraph
from ..tree import Tree


class WeightedDAG(DirectedAcyclicGraph):
    """
    add weight_data structure:
    {
        (a,b) : weight
    }
    """
    DIRECTED = True
    DEFAULT_WEIGHT = 1

    def __init__(self, graph_data=None, weight_data=None):
        """
        Initialize a graph.
        """
        super().__init__(graph_data=graph_data)
        self.weight_data = weight_data if weight_data is not None else {}

    def add_edge(self, edge, weight=None):
        """
        Add an directed edge to the graph connecting two nodes.
        """
        super(WeightedDAG, self).add_edge(edge)

        if weight is None:
            self.weight_data[edge] = self.DEFAULT_WEIGHT
        else:
            self.weight_data[edge] = weight

    def del_edge(self, edge):
        """
        Remove an directed edge from the graph.
        """
        super(WeightedDAG, self).del_edge(edge)

        del self.weight_data[edge]

    def set_edge_weight(self, edge, weight):
        self.weight_data[edge] = weight

    def edge_weight(self, edge):
        if edge not in self.weight_data:
            raise Exception(f'{edge} does not have data.')

        return self.weight_data[edge]

    def _init_costs(self, start):
        costs = {}
        for node in self.nodes():
            if node == start:
                costs[node] = 0
            else:
                costs[node] = float("inf")
        return costs

    @staticmethod
    def _find_lowest_cost_node(costs, processed):
        """
        start - node the total cost
        always return the lowest cost node.
        """
        lowest_cost = float("inf")
        lowest_cost_node = None

        for node, cost in costs.items():
            if cost < lowest_cost and node not in processed:
                lowest_cost = cost
                lowest_cost_node = node
        return lowest_cost_node

    def dijkstra_search(self, start):
        """
        return the shortest path tree
        """
        processed = []
        costs = self._init_costs(start)
        node = self._find_lowest_cost_node(costs, processed)
        spt = Tree(node)

        while node is not None:
            cost = costs[node]
            for sub_node in self.neighbors(node):
                new_cost = cost + self.edge_weight((node, sub_node))
                if costs[sub_node] > new_cost:
                    costs[sub_node] = new_cost

                    if spt.has_node(sub_node):
                        spt.remove_child(sub_node)
                    spt.insert_child(node, sub_node)

            processed.append(node)
            node = self._find_lowest_cost_node(costs, processed)

        return spt

    def dijkstra_shortest_path_search(self, start, end):
        processed = []
        costs = self._init_costs(start)
        node = self._find_lowest_cost_node(costs, processed)
        spt = Tree(node)

        while node is not None:
            cost = costs[node]
            for sub_node in self.neighbors(node):
                new_cost = cost + self.edge_weight((node, sub_node))
                if costs[sub_node] > new_cost:
                    costs[sub_node] = new_cost

                    if spt.has_node(sub_node):
                        spt.remove_child(sub_node)
                    spt.insert_child(node, sub_node)

            processed.append(node)
            node = self._find_lowest_cost_node(costs, processed)

            if node == end:
                break

        return spt

    def dijkstra_shortest_path(self, start, end):
        spt = self.dijkstra_shortest_path_search(start, end)
        min_path = spt.shortest_path_to(end)
        return [i.name for i in min_path]

