#!/usr/bin/env python
'''
Operate on ups.objects.Node objects
'''

def walk(node):
    '''An os.walk-like iteration on nodes

    Use like:

        for node, parents in walk(node):
            ...
    
    Nodes accessible by more than one path will be returned multiple times.

    '''

    yield node, []
    for child in node.children:
        for n,p in walk(child):
            yield n, [node] + p
    return
            
        

        
