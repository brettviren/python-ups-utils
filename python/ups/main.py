#!/usr/bin/env python
'''
A main CLI to the ups modules

'''

# This is kind of a mess right now

import os
import sys
import click

from ups.commands import UpsCommands, install as install_ups
from ups.products import product_to_upsargs, upsargs_to_product
import ups.tree

@click.group()
@click.option('-z','--products', envvar='PRODUCTS', multiple=True, type=click.Path(),
              help="UPS Product Directory to install into.")
@click.pass_context
def cli(ctx, products):
    '''UPS Utility Script'''
    ctx.obj['PRODUCTS'] = tuple(os.path.realpath(p) for p in products)
    ctx.obj['commands'] = uc = UpsCommands(ctx.obj['PRODUCTS'])
    ctx.obj['tree'] = ups.tree.Tree(uc)
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
    tree = ctx.obj['tree']
    for pd in tree.available():
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
    tree = ctx.obj['tree']
    pd = tree.resolve(package, version, qualifiers, flavor)
    if not pd:
        click.echo('no package found in %s' % str(tree.uc.products_path))
        sys.exit(1)
    click.echo(product_to_upsargs(pd))


@cli.command()
@click.option('-f','--flavor', help="Specify platform flavor")
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

    tree = ctx.obj['tree']
    pd = tree.resolve(package, version, qualifiers, flavor)
    if not pd:
        raise RuntimeError, 'Found no matching package: %s %s %s %s' % (package,version,qualifiers,flavor)

    graph = tree.dependencies([pd])

    # just dot for now
    from . import dot
    text = dot.simple(graph)
    open(output,'wb').write(text)
    return


@cli.command()
@click.pass_context
def top(ctx):
    '''
    List the top-level packages
    '''
    tree = ctx.obj['tree']
    ret = [product_to_upsargs(p) for p in sorted(tree.top())]
    click.echo('\n'.join(ret))
    
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



