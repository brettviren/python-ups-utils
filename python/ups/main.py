#!/usr/bin/env python
'''
A main CLI to the ups modules

'''

# This is kind of a mess right now

import os
import sys
import click

from networkx import nx

from ups.commands import UpsCommands, install as install_ups
from ups.products import product_to_upsargs, upsargs_to_product, make_product

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
    uc = ctx.obj['commands']
    for pd in uc.avail():
        click.echo(product_to_upsargs(pd))

@cli.command()
@click.option('-f','--flavor', 
              help="Limit the platform flavor")
@click.option('-q','--qualifiers', 
              help="Limit the build qualifiers with a colon-separated list")
@click.argument('package')
@click.argument('version')
@click.pass_context
def resolve(ctx, flavor, qualifiers, package, version):
    uc = ctx.obj['commands']
    flavor = flavor or uc.flavor()
    for pd in uc.avail():
        if pd.name != package: continue
        if pd.version != version: continue
        if pd.flavor != flavor: continue
        if set(pd.quals.split(":")) != set(qualifiers.split(":")): continue
        click.echo(product_to_upsargs(pd))
        break

@cli.command()
@click.option('-f','--flavor', 
              help="Specify platform flavor")
@click.option('-q','--qualifiers', 
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

    uc = ctx.obj['commands']
    tree = uc.full_dependencies()
    found = None
    for pd in tree.nodes():
        if pd.name != package: continue
        if pd.version != version: continue
        if pd.flavor != flavor: continue
        if set(pd.quals.split(":")) != set(qualifiers.split(":")): continue
        found = pd
        break
    if not found:
        click.echo('Found no product matching %s %s -f "%s"-q "%s"' % \
                   (pacakge, version, flavor, qualifiers))
        sys.exit(1)

    subtree = nx.DiGraph()
    subtree.add_edges_from(nx.bfs_edges(tree, found))

    if format == 'dot':
        from . import dot
        text = dot.simple(subtree)
        open(output,'wb').write(text)
        
    # raw
    print subtree.edges()


@cli.command()
@click.pass_context
def top(ctx):
    '''
    List the top-level packages
    '''
    uc = ctx.obj['commands']
    tree = uc.full_dependencies()
    top_nodes = set(tree.nodes())
    for edge in tree.edges():
        try:
            top_nodes.remove(edge[1])
        except KeyError:
            pass
    for p in top_nodes:
        click.echo(product_to_upsargs(p))
    
@cli.command()
@click.option('-n','--no-op', help="Dry run")
@click.argument('package')
@click.argument('version')
@click.pass_context
def purge(ctx, no_op, package, version):
    '''
    Return candidates for purging if the given product were removed.
    '''
    tree = ctx.obj['tree']
    pds = tree.match(name=package, version=version)
    if not pds:
        raise RuntimeError, 'No matches for name="%s" version="%s"' % (package,version)

    print 'Targeting:'
    for p in pds:
        print '\t%s' % str(p)
        assert p.repo

    tokill = tree.purge(pds)
    rmpaths = set()
    for dead in tokill:
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
    for path in sorted(rmpaths):
        print path

    

def main():
    cli(obj={}, auto_envvar_prefix='UU')



