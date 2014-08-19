#!/usr/bin/env python
'Wrappers around UPS commands'

import os
import tempfile
import tarfile
import urllib
from glob import glob
from subprocess import Popen, PIPE, check_call

import ups.products
import ups.depend

def install(version, products_dir, temp_dir = None):
    '''
    Install UPS <version> in <products_dir>, maybe using <temp_dir> to do the build.
    '''
    version_underscore = 'v' + version.replace('.','_')

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
    def __init__(self, path):
        '''Create a UPS command set.  

        The <path> argument is path of UPS product areas.
        '''
        if isinstance(path, type("")):
            path = path.split(":")
        self._products_path = path

    def ups(self, upscmdstr):
        '''
        Run a ups command string <upscmdstr> and return the full text output.  

        Eg: 

        .ups("list -aK+")
        '''
        return self.call(upscmdstr, cmd='ups')

    def call(self, cmdstr, cmd='ups'):
        cmdlist = list()

        for pdir in self._products_path:
            cmdlist.append(". %s/setups" % pdir)
        cmdlist.append(cmd + " " + cmdstr)
        line = ' && '.join(cmdlist)
        print 'UPS CMD:',line
        text = Popen(line, shell='/bin/bash', stdout = PIPE).communicate()[0]
        return text

    def flavor(self):
        '''Return the output of "ups flavor"'''
        return self.ups("flavor").strip()

    def depend(self, product):
        return self.ups("depend " + ups.products.product_to_upsargs(product))

    def avail(self):
        '''Return available products as set of Product objects.'''
        text = self.ups("list -aK+")
        ret = set()
        for line in text.split('\n'):
            line = line.strip()
            if not line: continue
            pd = ups.products.upslisting_to_product(line) # note, no repo on purpose
            ret.add(pd)
        return ret

    def full_dependencies(self):
        '''Return a tree of entire dependencies'''
        pds = self.avail()
        return ups.depend.full(self, pds)
