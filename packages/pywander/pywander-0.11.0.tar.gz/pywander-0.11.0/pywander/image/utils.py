import os
import logging
import click

logger = logging.getLogger(__name__)


def detect_output_file_exist(basedir, img_name, outputformat, overwrite):
    filename = '{}.{}'.format(img_name, outputformat)
    filename = os.path.join(basedir, filename)

    if os.path.exists(filename) and not overwrite:
        click.echo('output image file exists. i will give it up.')
        return None
    return filename

