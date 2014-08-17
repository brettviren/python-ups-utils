#!/usr/bin/env python
'''
Test using some example output from ups depend
'''

import os
from glob import glob
import ups.depend

testdir = os.path.dirname(os.path.realpath(__file__))

def test_parse_one():
    text = open(os.path.join(testdir, 'example-data/ups_v5_0_5__Linux64bit+2.6-2.12.dep')).read()
    graph = ups.depend.parse(text)
    

    import networkx as nx
    nx.write_gpickle(graph,'test_parse_one.pickle')
    
    graph2 = nx.read_gpickle('test_parse_one.pickle')
    print graph2.nodes()

def test_parse_all():

    for dep in glob(os.path.join(testdir, 'example-data/*.dep')):
        text = open(dep).read()
        graph = ups.depend.parse(text)
