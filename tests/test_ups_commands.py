#!/usr/bin/env python
'''
test ups.commands

WARNING: these tests will merely print a message and succeed if UPS is not detected.

'''

import os
from ups.commands import install, UpsCommands
from ups.products import make_product
import ups.tree

ups_version = '5.0.5'
ups_version_underscore = 'v' + ups_version.replace('.','_')
ups_products = os.path.realpath('products')

def setup():
    install(ups_version, ups_products)
    

def test_ups_depend():
    '''
    Test calling "ups depend".
    '''
    uc = UpsCommands(ups_products)

    prod = make_product('ups', ups_version_underscore, flavor=uc.flavor())
    #print 'PROD:',prod
    assert prod.flavor

    text = uc.depend_nocache(prod)
    assert text.startswith('ups v'), '"%s"'%text

    text2 = uc.depend(prod)
    assert text == text2, '"%s"\n!=\n"%s"' % (text, text2)

def test_ups_avail():
    '''
    Test calling "ups depend".
    '''
    uc = UpsCommands(ups_products)

    text = uc.avail()
    #print text

    

def test_ups_tree_match():
    uc = UpsCommands(ups_products)
    tree = ups.tree.Tree(uc)
    pds = tree.match(name='upd')
    assert len(pds) == 1
    pds = tree.match(name='u*')
    assert len(pds) == 0
    pds = tree.match(name='u.*')
    assert len(pds) == 2, pds
    assert "ups" in [p.name for p in pds]
    assert "upd" in [p.name for p in pds]
