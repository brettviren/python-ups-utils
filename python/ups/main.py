#!/usr/bin/env python
'''
A main CLI to the ups modules
'''

import os
import sys

from . import commands
from . import objects

def cli_install(*args):
    commands.install(*args)

def standard_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-f',dest='flavor', default='')
    parser.add_option('-z',dest='repo', default='')
    parser.add_option('-q',dest='quals', default='')
    return parser

def cli_depend(*args):
    parser = standard_options()
    o,a = parser.parse_args(list(args))
    pkg = a[0]
    try:
        ver = a[1]
    except IndexError:
        ver = ''
    pd = objects.ProdDesc(pkg, ver, o.flavor, o.repo, o.quals)
    print pd

    setups = ''
    if o.repo:
        setups = os.path.join(o.repo,'setups')
    return commands.depend(pd, setups)

def main():
    cmd = 'cli_' + sys.argv[1]
    meth = eval(cmd)
    args = sys.argv[2:]
    print meth(*args)

