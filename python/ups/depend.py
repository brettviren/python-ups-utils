#!/usr/bin/env python

import re

from objects import ProdDesc, Node

def parse_line(line):
    '''Parse one line from "ups depend".

    Return a tuple holding the depth of the line and a ProdDesc
    object.
    '''
    depth = 0
    if line.startswith('|'):
        m = re.match('([\| ]  )*\|__', line)
        if not m:
            raise ValueError, 'Failed to parse line: %s' % line
        pre = m.group(0)
        line = line[len(pre):]
        depth = len(pre)/3

    quals = None
    chunks = line.split()
    if len(chunks) == 6:
        pkg,ver, f,flav, z,path = chunks
    elif len(chunks) == 8:    
        pkg,ver, f,flav, z,path, q,quals = chunks
    else:
        raise ValueError, 'parse failure for line: %s' % str(chunks)
    return depth, ProdDesc(pkg, ver, flav, path, quals)

def parse(text):
    '''
    Parse text output from 'ups depend'.  

    Return sequence of ups.objects.Node with .payload holding ups.objects.ProdDesc.
    '''
    allnodes = list()
    parents = list()
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        depth, pd = parse_line(line)
        node = Node(pd)
        allnodes.append(node)
        
        if not parents:
            assert depth == 0
            parents.append(node)
            continue

        parents = parents[:depth]
        parents[-1].children.append(node)
        parents.append(node)

    return allnodes
