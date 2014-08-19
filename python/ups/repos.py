#!/usr/bin/env python
'''
Interact with UPS repositories
'''

import os
from glob import glob

import networkx as nx

from .products import make_product, upslisting_to_product
from . import depend


def dependency_tree(uc):
    '''
    Return the full dependency for the given UPS command set <uc>
    '''

        
        



class UpsRepo(object):
    '''A UpsRepo object embodies a snapshot of the state of a UPS
    products area.

    It consists of:

    - a directory
    - a user script to setup to use the "ups" command in that area
    - a number of products
    '''

    def __init__(self, directory):
        self._directory = directory
        self.uc = UpsCommands(os.path.join(directory, 'setups'))
        
        availtext = self.uc.avail()
        ret = set()
        for line in availtext.split('\n'):
            pd = upslisting_to_product(line)
            ret.add(pd)

        tree = nx.DiGraph()

    for pd in seeds:
        text = uc.depend(pd)
        ng = parse(text)
        tree.add_nodes_from(ng.nodes())
        tree.add_edges_from(ng.edges())

        self.tree = depend.full(self.uc, ret)
        
    def available(self):
        '''
        Return a list of available products in this repository, according to UPS.
        '''
        return self.tree.nodes()


















class UpsRepoObsolete(object):
    '''
    The UPS repository as a database.
    '''

    def __init__(self, products_path, verbose = False):
        if isinstance(products_path, type("")):
            products_path = products_path.split(":")
        self.products_path = [os.path.realpath(path) for path in products_path]
        self._verbose = verbose

    def chirp(self, msg):
        if self._verbose:
            print msg

    def available(self):
        '''
        Return list of Products objects available from the UPS products areas.
        '''
        ret = []
        for base in self.products_path:
            pdirs = glob(os.path.join(base, '*/*.version/*'))
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
        
    def find_product(self, package, version, qualifiers, flavor = 'any'):
        '''
        Return Product object matching args to UPS product area layout.
        '''
        avail = self.available() # fixme: maybe needs caching?

        want = set()
        if qualifiers:
            want = set(qualifiers.split(':'))

        for pd in avail:
            #self.chirp('find_product, check: "%s"' % str(pd))
            if pd.name != package:
                #self.chirp('\tname mismatch: "%s" != "%s"' %(pd.name, package))
                continue
            if pd.version != version:
                self.chirp('\tversion mismatch: "%s" != "%s"' %( pd.version, version))
                continue
            if pd.flavor != flavor:
                self.chirp('\tflavor mismatch "%s" != "%s"' %(pd.flavor, flavor))
                continue

            have = set()
            if pd.quals:
                have = set(pd.quals.split(":"))
            if have != want:
                self.chirp('\tquals mismatch "%s" != "%s"' %(want, have))
                continue
            return pd
