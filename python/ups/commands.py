#!/usr/bin/env python
'Wrappers around UPS commands'

import os
import tempfile
import tarfile
import urllib
from glob import glob
from subprocess import Popen, PIPE, check_call

from . import products

def install(version, products_dir, temp_dir = None):
    '''
    Install UPS <version> in <products_dir>, maybe using <temp_dir> to do the build.
    '''
    version_underscore = 'v' + version.replace('.','_')
    version_nodtos = version.replace('.','')

    if os.path.exists(os.path.join(products_dir, '.upsfiles')):
        return 'Already installed into directory: %s' % os.path.realpath(products_dir)

    if not os.path.exists(products_dir):
        os.makedirs(products_dir)

    temp_dir = temp_dir or tempfile.mkdtemp()
    os.path.exists(temp_dir) or os.makedirs(temp_dir)
    cwd = os.path.realpath(os.path.curdir)
    os.chdir(temp_dir)
    tarball = "ups-upd-%s-source.tar.bz2" % version
    if not os.path.exists(tarball):
        source_url = "http://oink.fnal.gov/distro/relocatable-ups/%s" % tarball
        urllib.urlretrieve(source_url, tarball)
    if not os.path.exists('.upsfiles'):
        tf = tarfile.open(tarball)
        tf.extractall()
        os.chdir('ups/' + version_underscore)
        check_call("./buildUps.sh " + temp_dir, shell='/bin/bash')
        check_call("./tarUpsUpd.sh " + temp_dir, shell='/bin/bash')
        os.chdir(temp_dir)

    kernel, _,_,_, machine = os.uname()
    want = "ups-upd-%s-%s*-%s.tar.bz2" % (version, kernel, machine)
    bintarball = glob(want)[0]
    tf = tarfile.open(bintarball)
    tf.extractall(products_dir)
    os.chdir(cwd)

class UpsCommands(object):
    def __init__(self, setups = None):
        '''Create a UPS command set.  

        <setups> may be a bash setup script to source before any UPS
        command is executed.  If not given the calling environment
        must already be configured to run the "ups" command.
        '''
        self._setups = setups

    def ups(self, upscmdstr):
        '''
        Run a ups command string <upscmdstr> and return the full text output.  

        Eg: 

        .ups("list -aK+")
        '''
        cmd = ""
        if self._setups:
            cmd += ". %s && " % self._setups
        cmd += "ups " + upscmdstr
        #print 'CMD:',cmd
        text = Popen(cmd, shell='/bin/bash', stdout = PIPE).communicate()[0]
        return text

    def flavor(self):
        '''Return the output of "ups flavor"'''
        return self.ups("flavor").strip()

    def depend(self, product):
        '''Run the "ups depend" command on the <product>'''
        return self.ups("depend " + products.product_to_upsargs(product))
        

    def avail(self):
        '''Run the "ups list" command and return the text'''
        text = self.ups("list -aK+")
        lines = [x for x in list(set(text.split('\n'))) if x]
        lines.sort()
        return '\n'.join(lines)


