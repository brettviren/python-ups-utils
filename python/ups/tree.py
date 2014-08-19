#!/usr/bin/env python
'''
Method for operating on the products tree
'''

from .repos import UpsRepo
from . import depend
from ups.products import product_to_upsargs, upsargs_to_product, upslisting_to_product

import networkx as nx

class Tree(object):
    def __init__(self, commands):
        self.uc = commands
        self.repo = UpsRepo(self.uc.products_path)

    def resolve(self, name ,version='', qualifiers='', flavor=''):
        return self.repo.find_product(name, version, qualifiers, flavor or self.uc.flavor())

    def dependencies(self, seeds = None):
        seeds = seeds or self.available()
        return depend.full(self.uc, seeds)

    def available(self):
        availtext = self.uc.avail()
        ret = set()
        for line in availtext.split('\n'):
            pd = upslisting_to_product(line)
            ret.add(pd)

        return ret

    def top(self):
        deps = self.dependencies()
        return depend.roots(deps)
        
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

