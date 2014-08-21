#!/usr/bin/env python
'''
test ups.commands

WARNING: these tests will merely print a message and succeed if UPS is not detected.

'''

import os
from ups.commands import install, UpsCommands
from ups.products import make_product

ups_version = '5.0.5'
ups_version_underscore = 'v' + ups_version.replace('.','_')
ups_products = os.path.realpath('products')

def setup():
    install(ups_version, ups_products)
    

def test_ups_flavor():
    uc = UpsCommands(ups_products)
    f = uc.flavor()
    assert f
    kern = os.uname()[0]
    assert f.startswith(kern)

def test_ups_depend():
    '''
    Test calling "ups depend".
    '''
    uc = UpsCommands(ups_products)

    prod = make_product('ups', ups_version_underscore, flavor=uc.flavor())
    #print 'PROD:',prod
    assert prod.flavor

    text = uc.depend(prod)
    assert text.startswith('ups v'), '"%s"'%text

    text2 = uc.depend(prod)
    assert text == text2, '"%s"\n!=\n"%s"' % (text, text2)

def test_ups_avail():
    '''
    Test calling "ups depend".
    '''
    uc = UpsCommands(ups_products)

    pds = uc.avail()
    #print '\n'.join([str(p) for p in sorted(pds)])
    for p in pds:
        assert not p.repo
        print p.name,p.version,p.flavor,p.quals

def test_ups_deps():
    uc = UpsCommands(ups_products)
    tree = uc.full_dependencies()
    assert 2 == len(tree.nodes())
    assert 0 == len(tree.edges())
    for pd in tree.nodes():
        assert pd.repo, str(pd)

def test_failure():
    uc = UpsCommands(ups_products)

    try:
        out = uc.call('',cmd='/bin/false')
    except RuntimeError,err:
        print 'Caught expected error: %s' % err
    else:
        raise Exception,'That command should have failed'
