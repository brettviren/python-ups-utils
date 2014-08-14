#!/bin/bash

# Download source and build UPS itself

# Note, this is just working out the steps.  The module
# ups.commands.install() and the CLI "ups-util install" do the
# equivalent.

set -o pipefail
set -o errtrace
set -o nounset
set -o errexit

version=$1 ; shift
products=$(readlink -f $1) ; shift

version_underscore=v$(echo $version | tr '.' '_')
version_nodots=$(echo $version | tr -d '.')

if [ ! -d build-ups ] ; then
    mkdir build-ups
fi
cd build-ups
top="$(pwd)"

# get
tarball="ups-upd-${version}-source.tar.bz2"
if [ ! -f "$tarball" ] ; then
    source_url="http://oink.fnal.gov/distro/relocatable-ups/$tarball"
    wget $source_url
fi
if [ ! -d .upsfiles ] ; then
    tar -xf $tarball
    cd ups/$version_underscore
    ./buildUps.sh $top
    ./tarUpsUpd.sh $top
fi

cd $top

bintarball="$(ls -t ups-upd-${version}-*-$(uname -m).tar.bz2|head)"
if [ ! -d "$products" ] ; then
    mkdir -p "$products"
fi
tar -C $products -xf $bintarball














# Let me just say, I hate everything about this.
