#!/usr/bin/env python
'''
Interact with UPS repositories
'''

import os
from glob import glob

from .products import make_product

class UpsRepo(object):
    '''
    The UPS repository as a database.
    '''

    def __init__(self, products_path):
        if isinstance(products_path, type("")):
            products_path = products_path.split(":")
        self.products_path = [os.path.realpath(path) for path in products_path]

    def available(self):
        '''
        Return list of Products objects available from the UPS products areas.
        '''
        ret = []
        for base in self.products_path:
            pdirs = glob(os.path.join(base, '*/v*.version/*'))
            for d in pdirs:
                sd = d[len(base)+1:]
                pkg,ver_version, flavor_quals_ = sd.split('/')
                assert ver_version.endswith('.version')
                ver = ver_version[:-len('.version')]
                flavor, quals_ = flavor_quals_.split('_',1)
                quals = ':'.join(quals_.split('_'))
                pd = make_product(pkg, ver, quals, base, flavor)
                ret.append(pd)
        return ret

    def setups_files(self, setups = 'setups'):
        '''
        Return the UPS "setups" file or None if not found
        '''
        ret = list()
        for base in self.products_path:
            maybe = os.path.join(base, setups)
            if os.path.exists(maybe):
                ret.append(maybe)
        return ret
        
    def find_product(self, package, version, qualifiers, flavor):
        '''
        Return Product object matching args to UPS product area layout.
        '''
        avail = self.available() # fixme: maybe needs caching?

        want = set()
        if qualifiers:
            want = set(qualifiers.split(':'))
        for pd in avail:
            #print 'find_product, check: "%s"' % str(pd)
            if pd.name != package:
                #print '\tname mismatch: "%s" != "%s"' %(pd.name, package)
                continue
            if pd.version != version:
                #print '\tversion mismatch: "%s" != "%"' %( pd.version, version)
                continue
            if pd.flavor != flavor:
                #print '\tflavor mismatch "%s" != "%s"' %(pd.flavor, flavor)
                continue

            have = set()
            if pd.quals:
                have = set(pd.quals.split(":"))
            if have != want:
                #print '\tquals mismatch "%s" != "%s"' %(want, have)
                continue
            return pd


# def pathify(path):
#     if isinstance(path, type("")):
#         path = path.split(":")
#     return path

# def find_setups(products, setups='setups'):
#     '''Return path to first instance of setups script in give products path.'''
#     for path in pathify(products):
#         maybe = os.path.join(path, setups)
#         if os.path.exists(maybe):
#             return maybe
#     return

# def find_product(product, package, version, qualifiers, flavor):
#     '''Return first matching product.'''
#     want = set()
#     if qualifiers:
#         want = set(qualifiers.split(':'))
    
#     for path in pathify(product):
#         stub = os.path.join(path, package, version + '.version', flavor)
#         for maybe in glob(stub + '_*'):
#             have = set([x for x in maybe[len(stub)+1:].split('_') if x])
#             if have == want:
#                 return make_product(package, version, qualifiers, path, flavor)
#         continue

        
        
    
