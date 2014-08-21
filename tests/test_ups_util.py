
from ups.manifest import parse_text as parse_manifest_text
import ups.util
import re

def test_match():
    flavor = 'Linux64bit+2.6-2.12'
    m = re.match(re.escape(flavor), flavor)
    assert m, m
    g = m.group()
    assert g
    assert g == m.string
    assert g == flavor

def test_match_mes():
    text = '''\
ups                  v5_1_2          ups-5.1.2-Linux64bit+2.6-2.12.tar.bz2                        -f Linux64bit+2.6-2.12                        
cmake                v2_8_12_2       cmake-2.8.12.2-slf6-x86_64.tar.bz2                           -f Linux64bit+2.6-2.12                        
gcc                  v4_8_2          gcc-4.8.2-slf6-x86_64.tar.bz2                                -f Linux64bit+2.6-2.12                        
boost                v1_55_0         boost-1.55.0-slf6-x86_64-e5-prof.tar.bz2                     -f Linux64bit+2.6-2.12     -q e5:prof         
fftw                 v3_3_3          fftw-3.3.3-slf6-x86_64-prof.tar.bz2                          -f Linux64bit+2.6-2.12     -q prof            
'''

    flavor = 'Linux64bit+2.6-2.12'
    quals = 'e5:prof'

    mes = parse_manifest_text(text)
    m = ups.util.match(mes, name='ups', version = 're:v*')
    assert len(m) == 0
    m = ups.util.match(mes, name='ups', version = 're:v.*')
    assert len(m) == 1
    m = ups.util.match(mes, name='ups', version = 're:v.*', flavor=flavor, quals=quals)
    assert len(m) == 0
    m = ups.util.match(mes, name='ups', version = 're:v.*', flavor=flavor)
    assert len(m) == 1, m


    
        
