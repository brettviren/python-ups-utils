#!/usr/bin/env python
'''Handle UPS/CET manifests

Manifests are text files containing a description of UPS binary
products making up a suite of software.
'''
from urllib.request import urlopen
from urllib.error import HTTPError
from collections import namedtuple

default_base_url="http://oink.fnal.gov/distro/manifest"
default_url_pattern = "{base_url}/{name}/{version}/{name}-{version_dotted}-{flavor}-{quals_dashed}_MANIFEST.txt"


ManifestEntry = namedtuple("ManifestEntry",'name version tarball flavor quals')

def make_manifest_entry(name, version, tarball, flavor='', quals=''):
    return ManifestEntry(name, version, tarball, flavor, quals)

def parse_line(line):
    '''
    Parse a manifest line returning a ManifestEntry
    '''
    line = line.strip()
    if not line:
        raise ValueError('No manifest line to parse')
    chunks = line.split(None,3)
    name,ver,tarball,rest = chunks


    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-f',dest='flavor', default='')
    parser.add_option('-q',dest='quals', default='')
    o,a = parser.parse_args(rest.split())
    return make_manifest_entry(name, ver, tarball, o.flavor, o.quals)

def form_url(product, base_url = default_base_url, url_pattern = default_url_pattern):
    '''
    Form a URL to a manifest for the give product.
    '''
    data = product._asdict()

    # take care of some capricious inconsistencies
    ver = product.version
    if ver.startswith('v'):
        ver = ver[1:]
    data['version_dotted'] = ver.replace('_','.')
    data['quals_dashed'] = product.quals.replace(':','-')

    return url_pattern.format(base_url = base_url, **data)

def download(url):
    '''
    Download manifest from given URL and return its text.
    '''
    try:
        fd = urlopen(url)
    except HTTPError:
        return None
    rc = fd.getcode() 
    if rc == 200:
        return fd.read().decode()
    
def parse_text(text):
    '''
    Parse a manifest's text into a list of ManifestEntry objects
    '''
    ret = list()
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        me = parse_line(line)
        ret.append(me)
    return ret

