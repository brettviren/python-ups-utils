#!/usr/bin/env python
'''
Test ups.depend
'''


root_dep = '''\
root v5_34_18d -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q e5:nu:prof
|__geant4 v4_9_6_p03b -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q e5:prof
|  |__clhep v2_1_4_1 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q e5:prof
|  |  |__gcc v4_8_2 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products
|  |__xerces_c v3_1_1a -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q e5:prof
|  |__g4emlow v6_32 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|  |__g4neutron v4_2 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|  |__g4neutronxs v1_2 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|  |__g4nucleonxs v1_1 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|  |__g4photon v3_0 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|  |__g4pii v1_3 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|  |__g4radiative v4_0 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|  |__g4surface v1_0 -f NULL -z /afs/rhic.bnl.gov/lbne/software/products
|__fftw v3_3_3 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q prof
|__gsl v1_16 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q prof
|__pythia v6_4_28a -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q gcc482:prof
|__postgresql v9_1_12 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products
|  |__python v2_7_6 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products
|     |__sqlite v3_08_03_00 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products
|__mysql_client v5_5_36 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q e5
|__libxml2 v2_9_1 -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q prof
|__xrootd v3_3_4a -f Linux64bit+2.6-2.12 -z /afs/rhic.bnl.gov/lbne/software/products -q e5:prof
'''

from ups.depend import parse
from ups.nodetools import walk as nodewalk

def dump(node):
    for n, rents in nodewalk(node):
        depth = len(rents)
        print '%s(%s %s)' % ('..'*depth, node.payload.name, node.payload.version)

def dump2(node):
    for n, rents in nodewalk(node):
        depth = len(rents)
        rents.append(n)
        print ''.join(['(%s %s)' % (x.payload.name, x.payload.version) for x in rents])

def test_parse_root():
    allnodes = parse(root_dep)
    top = allnodes[0]
    dump(top)
    dump2(top)
    for n in allnodes:
        print n[:-1]

def test_correct():
    allnodes = parse(root_dep)
    top = allnodes[0]

    assert len(top.children) == 8, '%s lost some children' % (top.payload.name)
    children_level1 = 'geant4 fftw gsl pythia postgresql mysql_client libxml2 xrootd'.split()
    for count, childname in enumerate(children_level1):
        assert top.children[count].payload.name == childname

