#!/usr/bin/env python
'''
test ups.nodetools
'''

from ups.nodetools import walk as nodewalk
from ups.objects import Node

def test_nodewalk():
    n1 = Node('n1')
    n2 = Node('n2',[n1])
    n3 = Node('n3',[n1])
    n4 = Node('n4',[n2,n3])
    for node, parents in nodewalk(n4):
        print node.payload, [p.payload for p in parents]

