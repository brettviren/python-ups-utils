#!/usr/bin/env python

import re

from collections import namedtuple

DepNode = namedtuple("DepNode",'name version flavor repo quals children')

def parse_line(line):
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
    if pkg == 'sqlite':
        print 'sqlite: depth=%d' % depth
    return depth, DepNode(pkg, ver, flav, path, quals, list())

def parse(text):
    '''
    Parse text output from 'ups depend'.  
    '''

    allnodes = list()
    parents = list()
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        depth, node = parse_line(line)
        allnodes.append(node)
        
        if not parents:
            assert depth == 0
            parents.append(node)
            continue

        parents = parents[:depth]
        parents[-1].children.append(node)
        parents.append(node)

    return allnodes


def dump(node, depth=0):
    print '%s(%s %s)' % ('..'*depth, node.name, node.version)
    for child in node.children:
        dump(child, depth+1)

def dump2(node, pre=''):
    mypre = "%s(%s %s)" % (pre, node.name, node.version)
    print mypre
    for child in node.children:
        dump2(child, mypre)
