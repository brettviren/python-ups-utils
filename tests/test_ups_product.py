#!/usr/bin/env python

from ups.products import Product


def test_operators():
    p1 = Product("foo","v1","a:b");
    p2 = Product("foo","v1","b:a");
    p3 = Product("foo","v1","c:b:a");
    p4 = Product("foo","v1");
    assert p1 == p2;
    assert p1 != p3;
    assert p1 != p4
    assert p2 != p3

    assert hash(p1) == hash(p2)

    col = [p1,p2,p3,p4]
    p5 = Product("foo","v1","a:c:b");
    assert p5 in col
    assert p5 == p3

def test_strings():
    p1 = Product("foo","v1","a:b");
    print (str(p1))
    print ('%s' % (p1,))
