#!/usr/bin/env python
'''
Test ups.manifest
'''

from ups.products import make_product
from ups.manifest import parse_line, form_url, download, parse_text

def test_parse_line():
    p1 = parse_line('ups                  v5_1_2          ups-5.1.2-Linux64bit+2.6-2.5.tar.bz2                         -f Linux64bit+2.6-2.5                         ')

    assert p1.name=='ups'
    assert p1.version=='v5_1_2', p1.version
    assert p1.tarball=='ups-5.1.2-Linux64bit+2.6-2.5.tar.bz2'
    assert p1.quals ==''
    assert p1.flavor == 'Linux64bit+2.6-2.5'

    p2 = parse_line('boost                v1_55_0         boost-1.55.0-slf5-x86_64-e5-prof.tar.bz2                     -f Linux64bit+2.6-2.5      -q e5:prof         ')
    assert p2.name=='boost'
    assert p2.version=='v1_55_0'
    assert p2.tarball=='boost-1.55.0-slf5-x86_64-e5-prof.tar.bz2'
    assert p2.flavor=='Linux64bit+2.6-2.5'
    assert p2.quals=='e5:prof'

def test_form_url():
    pd = make_product('nu', 'v1_10_00a', 'e5:prof', 'Linux64bit+2.6-2.5')
    want = 'http://oink.fnal.gov/distro/manifest/nu/v1_10_00a/nu-1.10.00a-Linux64bit+2.6-2.5-e5-prof_MANIFEST.txt'
    got = form_url(pd)
    if not got == want:
        print '\nWANT:"%s"\n GOT:"%s"' % (want, got)
    assert got == want


def test_download():
    url = 'http://oink.fnal.gov/distro/manifest/nu/v1_10_00a/nu-1.10.00a-Linux64bit+2.6-2.5-e5-prof_MANIFEST.txt'
    text = download(url)
    assert text.startswith('ups')
    man = parse_text(text)
    assert man[0].name == 'ups'
    assert man[0].version == 'v5_1_2'

    bad_url = 'http://oink.fnal.gov/distro/manifest/dne/v0_0_0/dne-0.0.0-Bland-unqualified-failure_MANIFEST.txt'
    text = download(bad_url)
    assert text is None

    
