#!/usr/bin/env python
'''
Data objects and methods for UPS products
'''

from collections import namedtuple

def Product(name, version='', quals="", repo="", flavor=""):
    '''Create an object holding information about a UPS product.'''
    P = namedtuple("Product",'name version quals repo flavor')
    return P(name, version, quals, repo, flavor)


def product_to_upsargs(pd):
    '''Return a string representation of the given product <pd> in a form
    used by UPS command line arguments.
    '''
    s = pd.name + ' ' + pd.version
    if pd.flavor:
        s += ' -f ' + pd.flavor
    if pd.repo:
        s += ' -z ' + pd.repo
    if pd.quals:
        s += ' -q ' + pd.quals
    return s


def upsargs_to_product(string):
    '''Convert from "pkg ver -f flav -z repo -q quals" to a Product'''
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-f',dest='flavor', default='')
    parser.add_option('-z',dest='repo', default='')
    parser.add_option('-q',dest='quals', default='')

    args = string.split()
    o,a = parser.parse_args(args)
    pkg = a[0]
    try:
        ver = a[1]
    except IndexError:
        ver = ''
    pd = Product(pkg, ver, o.quals, o.repo, o.flavor)
    return pd

def parse_prodlist(text):
    '''
    Convert the output of "ups list" to list of ProdDesc
    '''
    ret = list()
    for line in text.split('\n'):
        line =line.strip()
        if not line: continue
        ver,pkg,flav,quals,repo = [x.replace('"','') for x in line.split()]
        p = Product(ver, pkg, quals, repo, flav)
        ret.append(p)
    return ret

    
