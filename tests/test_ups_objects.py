#!/usr/bin/env python
'''
test ups.objects
'''

from ups.objects import ProdDesc, Node

def test_proddesc():
    pd = ProdDesc("package", "version", 'cherry', '/path/to/nowhere', 'low:rent')
    #print pd
    assert pd.quals == 'low:rent'
    assert pd.upsargs() == 'package version -f cherry -z /path/to/nowhere -q low:rent'

def test_node():
    n1 = Node()
    print n1
    n2 = Node('n2')
    print n2
    n3 = Node([1,2],[n2,n1])
    print n3
    n4 = Node('payload', [n3], a=1, b=2)
    print n4


