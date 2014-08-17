#!/usr/bin/env python
'''
A main CLI to the ups modules

'''

# This is kind of a mess right now

import os
import click

@click.group()
@click.option('-z','--products', envvar='PRODUCTS', multiple=True, type=click.Path(),
              help="UPS Product Directory to install into.")
@click.pass_context
def cli(ctx, products):
    '''UPS Utility Script'''
    ctx.obj['PRODUCTS'] = tuple(os.path.realpath(p) for p in products)
    pass

@cli.command()
@click.option('-t','--tmp', help="Use given temporary directory for building.")
@click.argument('version')
@click.pass_context
def init(ctx, tmp, version):
    '''Initialize a UPS products area including installation of UPS'''
    import ups.commands
    products = ctx.obj['PRODUCTS'][0] or '.'

    msg = ups.commands.install(version, products, tmp)
    if msg:
        click.echo(msg)

@cli.command()
@click.pass_context
def avail(ctx):
    '''List available UPS packages'''
    from ups.commands import UpsCommands
    from ups.repos import find_setups
    uc = UpsCommands(find_setups(ctx.obj['PRODUCTS']))
    text = uc.avail()
    click.echo(text)



@cli.command()
@click.option('-f','--flavor', help="Specify platform flavor")
@click.option('-q','--qualifiers', 
              help="Specify build qualifiers as colon-separated list")
@click.argument('package')
@click.argument('version')
@click.pass_context
def resolve(ctx, flavor, qualifiers, package, version):
    from ups.repos import find_setups, find_product
    from ups.commands import UpsCommands
    uc = UpsCommands(find_setups(ctx.obj['PRODUCTS']))
    pd = find_product(ctx.obj['PRODUCTS'], package, version, qualifiers, flavor or uc.flavor())
    click.echo(str(pd))


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
    format = format or os.path.splitext(output)[1][1:]
    if format not in ['raw','dot']:
        raise RuntimeError, 'Unknown format: "%s"' % format

    from ups.repos import find_setups, find_product
    from ups.commands import UpsCommands
    from ups import depend
    uc = UpsCommands(find_setups(ctx.obj['PRODUCTS']))
    flavor = flavor or uc.flavor()
    pd = find_product(ctx.obj['PRODUCTS'], package, version, qualifiers, flavor)
    if not pd:
        raise RuntimeError, 'Found no matching package: %s %s %s %s' % (package,version,qualifiers,flavor)
    text = uc.depend(pd)
    if format == 'raw':
        open(output,'wb').write(text)
        return

    graph = depend.parse(text)
    if format == 'dot':
        from . import dot
        text = dot.simple(graph)
        open(output,'wb').write(text)
        return

    assert None, 'How did I get here?'

# def cli_depend(*args):
#     pd = objects.parse_proddesc(' '.join(args))
#     setups = ''
#     if pd.repo:
#         setups = os.path.join(pd.repo,'setups')
#     return commands.depend(pd, setups)

def main():
    cli(obj={}, auto_envvar_prefix='UU')



# def cli_dot(*args):
#     '''
#     Return a GraphViz dot representation of the dependency graph
#     '''
#     setups = ""

#     allprods = []
#     if args:
#         pd = objects.parse_proddesc(' '.join(args))
#         allprods = [pd]
#         if pd.repo:
#             setups = os.path.join(pd.repo, 'setups')
#     else:
#         parser = OptionParser()
#         parser.add_option('-z',dest='repo', default='')
#         o,a = parser.parse_args(list(args))
#         if o.repo:
#             setups = os.path.join(o.repo, 'setups')
#         text = commands.avail(setups)
#         allprods = objects.parse_prodlist(text)

#     seenprods = list()
#     for prod in allprods:
        


#         text = commands.depend(pd, setups)
#         allnodes = depend.parse(text)



# def main():
#     cmd = 'cli_' + sys.argv[1]
#     meth = eval(cmd)
#     args = sys.argv[2:]
#     print meth(*args)



if __name__ == '__main__':
    main()
