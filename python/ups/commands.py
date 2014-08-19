#!/usr/bin/env python
'Wrappers around UPS commands'

import os
import tempfile
import tarfile
import urllib
from glob import glob
from subprocess import Popen, PIPE, check_call

from . import products
from .repos import UpsRepo

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
    def __init__(self, path, cache = '~/.ups-util/cache/'):
        '''Create a UPS command set.  

        The <path> argument is path of UPS product areas.
        '''
        if isinstance(path, type("")):
            path = path.split(":")
        self.products_path = path
        self.repo = UpsRepo(self.products_path)
        
        self._depcache = None
        if cache:
            cache = os.path.expanduser(os.path.expandvars(cache))
            if not os.path.exists(cache):
                os.makedirs(cache)
            #self._depcache = shelve.open(os.path.join(cache,'depcache'))
            self._depcache = os.path.join(cache,'depcache')

    def _product_ident(self, pd):
        '''
        Return a unique string for the product <pd>.
        '''
        if not pd.repo:
            new = self.repo.find_product(pd.name, pd.version, pd.quals, pd.flavor)
            if not new:
                new = self.repo.find_product(pd.name, pd.version, None, pd.flavor)
            assert new, 'Found no product: "%s"' % str(pd)
            pd = new
        ret = str(pd)
        return ret

    def ups(self, upscmdstr):
        '''
        Run a ups command string <upscmdstr> and return the full text output.  

        Eg: 

        .ups("list -aK+")
        '''
        return self.call(upscmdstr, cmd='ups')

    def call(self, cmdstr, cmd='ups', setups = None):
        cmdlist = list()

        if setups is None:
            setups = self.repo.setups_files()
        
        for script in setups:
            cmdlist.append(". " + script)
        cmdlist.append(cmd + " " + cmdstr)
        line = ' && '.join(cmdlist)
        print 'UPS CMD:',line
        text = Popen(line, shell='/bin/bash', stdout = PIPE).communicate()[0]
        return text

    def flavor(self):
        '''Return the output of "ups flavor"'''
        return self.ups("flavor").strip()

    def depend_nocache(self, product):
        return self.ups("depend " + products.product_to_upsargs(product))

    def depend(self, product):
        '''Run the "ups depend" command on the <product>'''
        if not self._depcache:
            return self.depend_nocache(product)

        ident = self._product_ident(product)
        import shelve
        cache = shelve.open(self._depcache)
        ret = cache.get(ident, None)
        if ret: 
            return ret
        ret = self.depend_nocache(product)
        cache[ident] = ret
        cache.close()
        return ret
        

    def avail(self):
        '''Run the "ups list" command and return the text'''
        text = self.ups("list -aK+")
        lines = [x for x in list(set(text.split('\n'))) if x]
        lines.sort()
        return '\n'.join(lines)


