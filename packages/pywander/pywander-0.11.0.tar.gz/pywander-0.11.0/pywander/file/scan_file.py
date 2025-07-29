import click

from pywander.path import gen_all_file2

def scan_file(root, filetype=""):
    for file_path in gen_all_file2(root, filetype=filetype):
        click.echo(file_path)