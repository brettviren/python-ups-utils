#!/usr/bin/env python
'''
Interact with UPS repositories
'''

import os
from glob import glob

from .products import Product

def find_setups(products, setups='setups'):
    '''Return path to first instance of setups script in give products path'''
    for path in products:
        maybe = os.path.join(path, setups)
        if os.path.exists(maybe):
            return maybe
    return

def find_product(product_path, package, version, qualifiers, flavor):
    '''Return first matching product.'''

    want = set()
    if qualifiers:
        want = set(qualifiers.split(':'))
    
    for path in product_path:
        stub = os.path.join(path, package, version + '.version', flavor)
        for maybe in glob(stub + '_*'):
            have = set([x for x in maybe[len(stub)+1:].split('_') if x])
            if have == want:
                return Product(package, version, qualifiers, path, flavor)
        continue

        
        
    
