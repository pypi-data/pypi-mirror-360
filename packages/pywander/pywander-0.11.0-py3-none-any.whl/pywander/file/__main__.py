import logging
import click

from .. import __version__
from pywander.file.run_py_file import batch_run_python_script
from pywander.file.scan_file import scan_file

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('pywander_file version {}'.format(__version__))
    ctx.exit()

def enable_debug(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    logging.basicConfig(level=logging.DEBUG)

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help="print this software version")
@click.option('-V', '--verbose', is_flag=True, is_eager=True,
              callback=enable_debug, expose_value=False,
              help='print verbose info')
def main():
    """
    pywander_file --version
    """
    pass

@main.command()
@click.argument('root')
@click.option('--filetype', default='', help="the filetype filter")
def scan(root, filetype):
    """
    扫描该目录下的文件

    scan  pywander --filetype py$

    ROOT: in which folder
    """
    scan_file(root=root, filetype=filetype)


@main.command()
@click.argument('root')
def run(root):
    """
    process all python file in which folder

    params:

    ROOT: in which folder
    """
    batch_run_python_script(root=root)


if __name__ == '__main__':
    main()