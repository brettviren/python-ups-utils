#!/usr/bin/env python
'''
test ups.commands

WARNING: these tests will merely print a message and succeed if UPS is not detected.

'''

import os
from ups.commands import depend, install

ups_version = '5.0.5'
ups_products = os.path.join(os.path.realpath('.'), 'products')
ups_setup = os.path.join(ups_products, 'setups')

def setup():
    install(ups_version, ups_products)
    

def test_ups_depend():
    '''
    Test calling "ups depend".
    '''
    import os

    from ups.objects import ProdDesc
    prod = ProdDesc('ups')
    text = depend(prod, setups = ups_setup)
    assert text.startswith('ups v')

