#!/usr/bin/env python
'''
Method for operating on the products tree
'''

from .repos import find_product
from . import depend
from ups.products import product_to_upsargs, upsargs_to_product

import networkx as nx

class Tree(object):
    def __init__(self, commands):
        self.uc = commands

    def resolve(self, name ,version='', qualifiers='', flavor=''):
        return find_product(self.uc.products, name, version, qualifiers, flavor or self.flavor())

    def dependencies(self, seeds = None):
        return depend.full(self.uc, seeds or self.available())

    def available(self):
        return set([upsargs_to_product(line) for line in self.uc.avail().split('\n')])

    def top(self):
        return depend.roots(self.dependencies())
        
    def purge(self, seeds):
        full_tree = self.dependencies()
        top = depend.roots(full_tree)

        dead = set(seeds)
        alive = top.difference(dead)

        dead_tree = nx.DiGraph()
        for n in dead:
            dead_tree.add_edges_from(nx.bfs_edges(full_tree, n))
        alive_tree = nx.DiGraph()
        for n in alive:
            alive_tree.add_edges_from(nx.bfs_edges(full_tree, n))

        return set(dead_tree.nodes()).difference(alive_tree.nodes())

