#!/usr/bin/env python
'''
A main CLI to the ups modules

'''

# This is kind of a mess right now

import os
import sys
import shutil
import click
import tempfile

from networkx import nx

from ups.commands import UpsCommands, install as install_ups
from ups.products import product_to_upsargs, upsargs_to_product, Product
import ups.repos
import ups.tree
import ups.util
import ups.mirror

@click.group()
@click.option('-z','--products', envvar='PRODUCTS', multiple=True, type=click.Path(),
              help="UPS Product Directory to install into.")
@click.pass_context
def cli(ctx, products):
    '''UPS Utility Script'''
    ctx.obj['PRODUCTS'] = tuple(os.path.realpath(p) for p in products)
    ctx.obj['commands'] = uc = UpsCommands(ctx.obj['PRODUCTS'])
    pass

@cli.command()
@click.option('-t','--tmp', 
              help="Use given temporary directory for building.")
@click.option('-v','--version',default = '5.1.5',
              help = "Version of UPS to use to prime the repository.")
@click.pass_context
def init(ctx, tmp, version):
    '''Initialize a UPS products area including installation of UPS'''
    products = ctx.obj['PRODUCTS'][0] or '.'
    if version.startswith('v'):
        version = version[1:].replace('_','.')
    msg = install_ups(version, products, tmp)
    if msg:
        click.echo(msg)

@cli.command()
# note: don't set a default flavor
@click.option('-f','--flavor', 
              help="Specify platform flavor")
# note: don't set explicit default qualifiers
@click.option('-q','--qualifiers', default='',
              help="Specify build qualifiers as colon-separated list")
@click.option('-F','--format', default = 'raw', type=click.Choice(['raw','dot']),
              help="Specify output format")
@click.option('-o','--output', default = '/dev/stdout', type=click.Path(),
              help="Specify output file")
@click.option('--full', 'full', default=False, flag_value=True, 
              help="Produce the full dependency tree instead of a minimal (single-path) graph.")
@click.argument('package')
@click.argument('version')
@click.pass_context
def depend(ctx, flavor, qualifiers, format, output, full, package, version):
    '''
    Product dependency information for the given product.
    '''
    format = format or os.path.splitext(output)[1][1:]
    if format not in ['raw','dot']:
        raise RuntimeError('Unknown format: "%s"' % format)

    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    tree = ups.repos.squash_trees(repos)

    flavor = flavor or repos[0].uc.flavor()
    seed = Product(package, version, qualifiers, flavor)
    subtree = nx.DiGraph()
    subtree.add_node(seed)
    subtree.add_edges_from(nx.bfs_edges(tree, seed)) # this is a minimal rep
    if full:
        sg = tree.subgraph(subtree.nodes())
        subtree.add_edges_from(sg.edges())

    if format == 'dot':
        from . import dot
        text = dot.simple(subtree)
        open(output,'wb').write(text.encode('utf-8'))
        
    # raw
    print ('%d nodes, %d edges' % (len(subtree.nodes()), len(subtree.edges())))


@cli.command()
@click.pass_context
def top(ctx):
    '''
    List the top-level packages
    '''
    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    tree = ups.repos.squash_trees(repos)
    top_nodes = ups.tree.top_nodes(tree)

    for p in sorted(top_nodes):
        p = ups.repos.first_pvqf(repos, *p[:4])
        click.echo(product_to_upsargs(p))
    
@cli.command()
@click.option('--dryrun/--no-dryrun', default=False, help="Dry run")
@click.argument('package')
@click.argument('version')
@click.pass_context
def purge(ctx, dryrun, package, version):
    '''
    Return candidates for purging if the given product were removed.

    The <package> and <version> string may be prefaced with 're:' to
    indicate that they should be interpreted as regular expressions
    (not globs).  Otherwise they will be literally matched.
    '''
    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    tree = ups.repos.squash_trees(repos)
    pds = ups.util.match(tree.nodes(), name=package, version=version)
    if not pds:
        raise RuntimeError('No matches for name="%s" version="%s"' % (package,version))

    #click.echo('Purging based on:')
    #for pd in pds:
    #    click.echo('\t'+str(pd))

    tokill = ups.tree.purge(tree, pds)
    rmpaths = set()
    for dead in tokill:
        dead = ups.repos.first_pvqf(repos, *dead[:4])
        path = os.path.join(dead.repo, dead.name, dead.version)        
        if not os.path.exists(path):
            click.echo('warning: no such product directory: %s' % path)
            continue
        rmpaths.add(path)
        vpath = path + '.version'
        if not os.path.exists(vpath):
            click.echo('warning: no such version directory: %s' % vpath)
            continue
        rmpaths.add(vpath)

    if dryrun:
        for path in sorted(rmpaths):
            click.echo(path)
        return

    # actually do the deed
    for path in sorted(rmpaths):
        print ('removing: %s' % path)
        shutil.rmtree(path)



@cli.command('manifest-urls')
@click.option('-m','--mirror', default='scisoft',
              help="Specify a mirror name")
@click.option('-l','--limit', multiple=True,
              help="Limit to one or more suites")
@click.pass_context
def manifest_urls(ctx, mirror, limit):
    print ('Limiting: %s' % limit)
    manifests = ups.mirror.find_manifests(mirror, limit)
    if not manifests:
        click.echo('No manifests for mirror "%s" %s' % (mirror, ', '.join(limit)))
        return
    click.echo('\n'.join(manifests))


@cli.command('manifest')
@click.option('-m','--mirror', default='scisoft',
              help="Specify a mirror name")
@click.option('-f','--flavor',
              help="Specify platform flavor")
@click.option('-q','--qualifiers', default='',
              help="Specify build qualifiers as colon-separated list")
@click.argument('suite')
@click.argument('version')
@click.pass_context
def dump_manifest(ctx, mirror, flavor, qualifiers, suite, version):
    '''
    Dump a manifest
    '''
    mir = ups.mirror.make(mirror)
    if not mir:
        click.echo('No such mirror: "%s"' % mirror)
        sys.exit(1)
    matmes = mir.load_manifest(suite, version, flavor, qualifiers)
    for me in matmes:
        click.echo('%16s %16s %20s %s' % (me.name, me.version, me.flavor, me.quals))


@cli.command('install')
@click.option('--dryrun', 'dryrun', default=False, flag_value=True, 
              help="Dry run, do not modify the repository")
@click.option('-m','--mirror', default='scisoft',
              help="Specify a mirror name")
@click.option('-f','--flavor',
              help="Specify platform flavor")
@click.option('-q','--qualifiers', default='',
              help="Specify build qualifiers as colon-separated list")
@click.option('--force', 'force', default=False, flag_value=True,
              help='Add even if already installed')
@click.option('-t','--tmp', 
              help="Use given temporary directory for building.")
@click.argument('suite')
@click.argument('version')
@click.pass_context
def install(ctx, dryrun, mirror, flavor, qualifiers, force, tmp, suite, version):
    '''Install a suite worth of packages from a suite to first configured repository.

    Note, qualifiers should match the suite's qualifier list
    '''
    repodir = ctx.obj['PRODUCTS'][0]
    if not version.startswith('v') and version.count('.') > 0:
        # it looks like we got a dotted version
        version = 'v' + version.replace('.','_')

    # there are lots of conventions for qualifiers delimiters in use
    # by Fermilab.  This uses :'s
    qualifiers = qualifiers.replace('-',':').replace('-',':')
        
    uc = ctx.obj['commands']
    flavor = flavor or uc.flavor()
    mir = ups.mirror.make(mirror)
    if not mir:
        click.echo('No such mirror: "%s"' % mirror)
        sys.exit(1)
    matmes = mir.load_manifest(suite, version, flavor, qualifiers)

    if dryrun:
        print ('Dry-run, not installing these %d products' % len(matmes))
        for me in matmes:
            pd = Product(me.name, me.version, me.quals, me.flavor, repodir)
            if uc.exists(pd):
                print ('\t%s -> %s (exists)' % (me.tarball, repodir))
                continue
            print ('\t%s -> %s' %(me.tarball, repodir))
        return

    if not tmp:
        tmpdir = tempfile.mkdtemp()
    else:
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        tmpdir = tmp

    # fixme: move this block into the a module
    # fixme: break this into full download-first before unpack?
    repo = ups.repos.UpsRepo(repodir)

    for me in matmes:
        pd = Product(me.name, me.version, me.quals, me.flavor, repodir)
        if uc.exists(pd):
            print ('\t%s -> %s/%s (skipped, exists)' %(mirror, tmpdir, me.tarball))
            print ('\t%s -> %s (skipped, exists)' % (me.tarball, repodir))
            continue
        print ('\t%s -> %s/%s' %(mirror, tmpdir, me.tarball))
        tfile = mir.download(me, tmpdir)
        print ('\t%s -> %s' %(me.tarball, repodir))
        repo.unpack(me, tfile)

    

@cli.command('view')
@click.option('--action', default = 'symlink',
                  type=click.Choice(['symlink', 'hardlink', 'copy', 'remove']),
                  help="Specify what to do to the view")
@click.option('-e','--exclude', multiple=True,
                  help="Exclude products matching given regex from the action")
@click.option('--dependencies/--no-dependencies', default=True,
                  help="Recurse the action down the dependency tree")
@click.option('-q','--quals', default='',
              help="Specify build qualifiers as colon-separated list")
@click.argument('package')
@click.argument('version')
@click.argument('path')
@click.pass_context
def view(ctx, action, exclude, dependencies, quals, package, version, path):
    '''
    Act on a view at given path of the UPS products area with given
    package/version at the top of the dependency tree.
    '''

    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    tree = prods = ups.repos.squash_trees(repos)

    # fixme: deal with flavor?e14:prof
    #flavor = flavor or repos[0].uc.flavor()
    want = Product(package, version, quals)

    prods = [p for p in prods if p.name == want.name]
    if len(prods) > 1:
        prods = [p for p in prods if p.version == want.version]
    if len(prods) > 1:
        prods = [p for p in prods if p.quals == want.quals]
    if len(prods) == 0:
        click.echo("No matching package: %s" % (want,))
        return 1
    if len(prods) > 1:
        click.echo("No uniquely matching package: %s" (want,))
        click.echo("\n".join(map(str,prods)))
        return 1
    seed = prods[0]
    click.echo("Found: %s" % (seed,))
    uc = ctx.obj['commands']
    uenv = uc.userenv(seed)
    for var,path in [('PATH','bin'), ('LD_LIBRARY_PATH','lib')]:
        click.echo(var)
        for one in uenv[var].split(':'):
            repo = None
            for r in repos:
                if one.startswith(r._repo_dir):
                    repo = r
                    break
            if not repo:
                continue
            # now link it into path
            click.echo('\t' + one)
                            

    # prods = nx.algorithms.descendants(tree, seed)
    # prods.add(seed)
    # for p in sorted(prods):
    #     click.echo(str(p))


def main():
    cli(obj={}, auto_envvar_prefix='UU')



