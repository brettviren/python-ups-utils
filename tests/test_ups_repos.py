#!/usr/bin/env python
'''
Test ups.repos
'''

import ups.repos

def test_repos():
    repo = ups.repos.UpsRepo('products')
    avail = repo.available()
    assert avail
    assert 2 == len(avail)
    print '\n'.join([str(p) for p in avail])

