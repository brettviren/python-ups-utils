#!/usr/bin/env python
'''
Test ups.repos
'''

import ups.repos

def test_avail():
    repo = ups.repos.UpsRepo('products')
    avail = repo.available()
    assert avail
    assert 2 == len(avail)
    print '\n'.join([str(p) for p in avail])


def test_setups():    
    repo = ups.repos.UpsRepo('products')
    ss = repo.setups_files()
    assert len(ss) == 1
    assert ss[0].endswith('setups')
    print ss

def test_product():
    repo = ups.repos.UpsRepo('products')
    repo.find_product('ups', 'v5_0_5', '', 'Linux64bit+2.6-2.12')
