#!/usr/bin/env python
'''Simple wrapper for UPS commands

It is assumed the calling process has "ups" in the PATH and otherwise
setup properly.

'''

import os
from subprocess import check_output, check_call


def install(version, products_dir, temp_dir = None):
    '''
    Install UPS <version> in <products_dir>, maybe using <temp_dir> to do the build.
    '''
    import tempfile
    import tarfile
    from glob import glob

    version_underscore = 'v' + version.replace('.','_')
    version_nodtos = version.replace('.','')

    if os.path.exists(os.path.join(products_dir, '.upsfiles')):
        return

    if not os.path.exists(products_dir):
        os.makedirs(products_dir)

    temp_dir = temp_dir or tempfile.mkdtemp()
    os.path.exists(temp_dir) or os.makedirs(temp_dir)
    cwd = os.path.realpath(os.path.curdir)
    os.chdir(temp_dir)
    tarball = "ups-upd-%s-source.tar.bz2" % version
    if not os.path.exists(tarball):
        import urllib
        source_url = "http://oink.fnal.gov/distro/relocatable-ups/%s" % tarball
        urllib.urlretrieve(source_url, tarball)
    if not os.path.exists('.upsfiles'):
        tf = tarfile.open(tarball)
        tf.extractall()
        os.chdir('ups/' + version_underscore)
        check_call("./buildUps.sh " + temp_dir,shell='/bin/bash')
        check_call("./tarUpsUpd.sh " + temp_dir,shell='/bin/bash')
        os.chdir(temp_dir)

    kernel, _,_,_, machine = os.uname()
    want = "ups-upd-%s-%s*-%s.tar.bz2" % (version, kernel, machine)
    bintarball = glob(want)[0]
    tf = tarfile.open(bintarball)
    tf.extractall(products_dir)
    os.chdir(cwd)

def depend(proddesc, setups=None):
    '''Run the "ups depend" command on the product described by
    <proddesc> and return the resulting text

    If <setups> is given it is interpreted as a UPS setup script.
    '''
    cmd = ""
    if setups:
        cmd = "source %s && " % setups
    cmd += "ups depend " + proddesc.upsargs()
    text = check_output(cmd, shell='/bin/bash')
    return text


