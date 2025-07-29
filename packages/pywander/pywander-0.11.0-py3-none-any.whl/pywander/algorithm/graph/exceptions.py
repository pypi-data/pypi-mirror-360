#!/usr/bin/env python
# -*-coding:utf-8-*-


class GraphError(Exception):
    """
    A base-class for the various kinds of errors that occur in the the graph class.
    """
    pass


class AdditionError(GraphError):
    """
    This error is raised when trying to add a node or edge already added
    to the graph or digraph.
    """
    pass


class NotAcyclicError(GraphError):
    """
    not acyclic graph error
    """
    pass
