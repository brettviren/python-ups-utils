#!/usr/bin/env python
'''
Test using some example output from ups depend without actually using ups
'''

import os
from glob import glob
import networkx as nx

import ups.depend
from ups.products import make_product, upsargs_to_product, product_to_upsargs
import ups.tree


testdir = os.path.dirname(os.path.realpath(__file__))


class FakeUC(object):
    products_path = ('products',)

    def __init__(self, data_dir = os.path.join(testdir, 'example-data')):
        self.data_dir = data_dir
        return

    def flavor(self):
        return 'Linux64bit+2.6-2.12'

    def find_dump_file(self, pd):
        quals = pd.quals or ''
        if quals == 'current': quals = '' # ???
        fname = '%s_%s_%s_%s.dep' % (pd.name, pd.version or '', quals, pd.flavor or '')
        return os.path.join(self.data_dir, fname)

    def avail(self):
        products = list()
        for cmdfile in glob(os.path.join(self.data_dir, '*.cmd')):
            cmd = open(cmdfile).read()
            pd = upsargs_to_product(cmd[len('ups_depend '):])
            products.append(pd)
        return '\n'.join([product_to_upsargs(p) for p in products])

    def depend(self, pd):
        fname = self.find_dump_file(pd)
        return open(fname).read()

def test_flavor():
    '''
    Make sure this platform has a doctored UPS flavor
    '''
    uc = FakeUC()
    print ("flavor is %s" % uc.flavor())

def test_parse_one():
    uc = FakeUC()
    pd = make_product('ups', 'v5_0_5', flavor='Linux64bit+2.6-2.12')
    deptext = uc.depend(pd)
    graph1 = ups.depend.parse(deptext)

    nx.write_gpickle(graph1,'test_parse_one.pickle')
    graph2 = nx.read_gpickle('test_parse_one.pickle')
    for g1, g2 in zip(graph1.nodes(), graph2.nodes()):
        assert g1 == g2

def graph_ref_list(graph):
    ret = list()
    for pd,attr in graph.nodes(data=True):
        number = attr.get('ref',0)
        ret.append((number, pd.name, pd.version))
    ret.sort()
    return ret
        

def test_parse_all():
    uc = FakeUC()
    available = [upsargs_to_product(line) for line in uc.avail().split('\n')]
    full_tree = ups.depend.full(uc, available)
    assert 1056 == full_tree.size()

    top = ups.depend.roots(full_tree)
    print ('Top:\n', '\n'.join(['\t%s %s' % (p.name, p.version) for p in sorted(top)]))
    assert 54 == len(top)

    dead = set([n for n in top if n.name == 'lbnecode' and n.version.startswith('v02_00')])
    assert 2 == len(dead)

    alive = top.difference(dead)
    assert 52 == len(alive)

    print ('%d dead, %d alive, %d top' % \
        (len(dead), len(alive), len(top)))

    dead_tree = nx.DiGraph()
    for n in dead:
        dead_tree.add_edges_from(nx.bfs_edges(full_tree, n))
    alive_tree = nx.DiGraph()
    for n in alive:
        alive_tree.add_edges_from(nx.bfs_edges(full_tree, n))

    tokill = set(dead_tree.nodes()).difference(alive_tree.nodes())
    assert 12 == len(tokill)

    tolive = set(alive_tree.nodes()).difference(dead_tree.nodes())
    assert 201 == len(tolive)

    print ('%d to kill, %d to live, %d all' % \
        (len(tokill), len(tolive), full_tree.size()))
    print ('Top to kill:\n', '\n'.join(['\t%s %s' % (p.name, p.version) for p in sorted(dead)]))
    print ('To kill:\n', '\n'.join(['\t%s %s' % (p.name, p.version) for p in sorted(tokill)]))
    

def _test_resolve():
    tree = ups.tree.Tree(FakeUC())

    package, version, qualifiers, flavor = ['larsoft', 'v02_00_00', 'e5:prof', 'Linux64bit+2.6-2.12']
    pd = tree.resolve(package, version, qualifiers, flavor)
    if not pd:
        raise RuntimeError('Found no matching: p=%s v=%s q=%s f=%s' % (package,version,qualifiers,flavor))


def _test_purge():
    tree = ups.tree.Tree(FakeUC())

    package, version, qualifiers, flavor = ['larsoft', 'v02_00_00', 'e5:prof', 'Linux64bit+2.6-2.12']
    pd = tree.resolve(package, version, qualifiers, flavor)
    if not pd:
        raise RuntimeError('Found no matching package: %s %s %s %s' % (package,version,qualifiers,flavor))
    tokill = tree.purge([pd])
    ret = [product_to_upsargs(p) for p in sorted(tokill)]
    print (tokill)
    
