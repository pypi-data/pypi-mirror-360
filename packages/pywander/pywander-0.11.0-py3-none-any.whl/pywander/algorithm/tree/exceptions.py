#!/usr/bin/env python
# -*-coding:utf-8-*-


class TreeError(Exception):
    """
    A base-class for the various kinds of errors that occur in the the tree class.
    """


class InsertError(TreeError):
    """
    This error is raised when you trying to insert a node in a tree
    which is already exists.
    """
