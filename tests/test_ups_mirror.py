#!/usr/bin/env python
'''
Test ups.mirror
'''

import os
import time
import shutil
import tarfile
import tempfile

import ups.mirror
import ups.util

def _test_oink():
    '''
    Test the "oink" mirror
    '''
    tdir = tempfile.mkdtemp(prefix='ups-mirror-test-oink-')
    print ('Using cache in: %s' % tdir)
    oink = ups.mirror.make('oink', cachedir=tdir)

    a = oink.avail()
    assert len(a) == 0

    mfdata = ('lbne','v02_05_01', 'Linux64bit+2.6-2.12', 'e5:prof')

    t0 = time.time()
    l1 = oink.load_manifest(*mfdata)
    t1 = time.time()
    l2 = oink.load_manifest(*mfdata)
    t2 = time.time()

    print ('Load %d in %f seconds and %d in %f seconds' % (len(l1), t1-t0, len(l2), t2-t1))
    assert len(l1) == len(l2)
    assert l1 == l2
    
    upses = ups.util.match(l1, name='ups')
    assert len(upses) == 1

    lars = ups.util.match(l1, name='re:lar.*')
    assert 12 == len(lars)

    
    target = oink.download(upses[0], tdir)
    assert target, upses[0]
    assert os.path.exists(target)

    s = os.stat(target)
    assert s
    assert s.st_size == 1184838
    
    assert tarfile.is_tarfile(target)

    shutil.rmtree(tdir)
