#!/usr/bin/env python
'''
Define general objects used throughout the ups. namespace.
'''

from collections import namedtuple

def ProdDesc(name, version='', flavor="", repo="", quals=""):
    PD = namedtuple("ProdDesc",'name version flavor repo quals')
    def argify(self):
        s = self.name + ' ' + self.version
        if self.flavor:
            s += ' -f ' + self.flavor
        if self.repo:
            s += ' -z ' + self.repo
        if self.quals:
            s += ' -q ' + self.quals
        return s
    PD.upsargs = argify

    return PD(name,version,flavor,repo,quals)

def Node(payload = None, children = None, **kwds):
    N = namedtuple("Node", 'payload children params')
    return N(payload or list(), children or list(), kwds)


