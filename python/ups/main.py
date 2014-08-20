#!/usr/bin/env python
'''
A main CLI to the ups modules

'''

# This is kind of a mess right now

import os
import sys
import shutil
import click

from networkx import nx

from ups.commands import UpsCommands, install as install_ups
from ups.products import product_to_upsargs, upsargs_to_product, make_product
import ups.repos
import ups.tree

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
@click.option('-t','--tmp', help="Use given temporary directory for building.")
@click.argument('version')
@click.pass_context
def init(ctx, tmp, version):
    '''Initialize a UPS products area including installation of UPS'''
    products = ctx.obj['PRODUCTS'][0] or '.'
    msg = install_ups(version, products, tmp)
    if msg:
        click.echo(msg)

@cli.command()
@click.pass_context
def avail(ctx):
    '''List available UPS packages'''
    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    pds = ups.repos.first_avail(repos)
    for pd in sorted(pds):
        click.echo(product_to_upsargs(pd))

@cli.command()
@click.option('-f','--flavor', 
              help="Limit the platform flavor")
@click.option('-q','--qualifiers', default='',
              help="Limit the build qualifiers with a colon-separated list")
@click.argument('package')
@click.argument('version')
@click.pass_context
def resolve(ctx, flavor, qualifiers, package, version):
    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    pd = ups.repos.first_pvqf(repos, package, version, qualifiers, flavor)
    if pd:
        click.echo(product_to_upsargs(pd))
    return

@cli.command()
@click.option('-f','--flavor', 
              help="Specify platform flavor")
@click.option('-q','--qualifiers', default='',
              help="Specify build qualifiers as colon-separated list")
@click.option('-F','--format', default = 'raw', type=click.Choice(['raw','dot']),
              help="Specify output format")
@click.option('-o','--output', default = '/dev/stdout', type=click.Path(),
              help="Specify output file")
@click.argument('package')
@click.argument('version')
@click.pass_context
def depend(ctx, flavor, qualifiers, format, output, package, version):
    '''
    Product dependency information for the given product.
    '''
    format = format or os.path.splitext(output)[1][1:]
    if format not in ['raw','dot']:
        raise RuntimeError, 'Unknown format: "%s"' % format

    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    tree = ups.repos.squash_trees(repos)

    seed = make_product(package, version, qualifiers, flavor)
    subtree = nx.DiGraph()
    subtree.add_node(seed)
    subtree.add_edges_from(nx.bfs_edges(tree, seed)) # this is a minimal rep

    if format == 'dot':
        from . import dot
        text = dot.simple(subtree)
        open(output,'wb').write(text)
        
    # raw
    print '%d nodes, %d edges' % (len(subtree.nodes()), len(subtree.edges()))


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
    '''
    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    tree = ups.repos.squash_trees(repos)
    pds = ups.tree.match(tree.nodes(), name=package, version=version)
    if not pds:
        raise RuntimeError, 'No matches for name="%s" version="%s"' % (package,version)

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
            print 'rm -rf %s' % path
        return

    # actually do the deed
    for path in sorted(rmpaths):
        print 'removing: %s' % path
        shutil.rmtree(path)

def main():
    cli(obj={}, auto_envvar_prefix='UU')



