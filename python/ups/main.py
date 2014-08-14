#!/usr/bin/env python
'''
A main CLI to the ups modules
'''

import sys

from . import commands

def main():
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    meth = getattr(commands, cmd)
    print meth(*args)

