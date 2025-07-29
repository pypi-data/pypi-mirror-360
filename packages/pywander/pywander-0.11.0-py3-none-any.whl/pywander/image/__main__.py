#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging
import click

from .. import __version__
from .resize_image import resize_image
from .convert_image import convert_image


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('pywander_image version {}'.format(__version__))
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
    pywander_image --version
    """
    pass


@main.command()
@click.option('-V', '--verbose', is_flag=True, is_eager=True,
              callback=enable_debug, expose_value=False,
              help='print verbose info')
@click.argument('inputimgs', type=click.Path(), nargs=-1, required=True)
@click.option('--width', default=0, type=int, help="the output image width")
@click.option('--height', default=0, help="the output image height")
@click.option('--outputdir', default="", help="the image output directory")
@click.option('--outputname', default="", help="the image output name")
def resize(inputimgs, width, height, outputdir, outputname):
    """
    调整图片尺寸，保持图片的长宽比。

    宽度高度只需要指定一个即可，另外一个会自动计算得到。
    """

    for input_img in inputimgs:
        output_img = resize_image(input_img, width=width, height=height,
                                 outputdir=outputdir, outputname=outputname)

        if output_img:
            click.echo("process: {} done.".format(input_img))
        else:
            click.echo("process: {} failed.".format(input_img))


@main.command()
@click.option('-V', '--verbose', is_flag=True, is_eager=True,
              callback=enable_debug, expose_value=False,
              help='print verbose info')
@click.argument('inputimgs', type=click.Path(), nargs=-1, required=True)
@click.option('--dpi', default=150, type=int, help="the output image dpi")
@click.option('--imgformat', default="png", help="the output image format")
@click.option('--outputdir', default="", help="the image output dir")
@click.option('--outputname', default="", help="the image output name")
@click.option('--overwrite/--no-overwrite', default=True,
              help='overwrite the output image file, default is overwrite')
@click.option('--transparent', is_flag=True,
              help="pdf convert to png|tiff can turn transparent on")
def convert(inputimgs, dpi, imgformat, outputdir, outputname, overwrite, transparent=False):
    """
    图片格式转换

    support image format: \n
      - pillow : png <-> jpg <-> gif <-> eps <-> tiff <-> bmp <-> ppm \n
      - inkscape: svg |svgz -> pdf | png | ps | eps \n
      - pdftocairo: pdf -> png | jpeg | ps | eps | svg \n
    """
    for input_img in inputimgs:
        output_img = convert_image(input_img, outputformat=imgformat, dpi=dpi,
                                  outputdir=outputdir, outputname=outputname,
                                  overwrite=overwrite, transparent=transparent)

        if output_img:
            click.echo("process: {} done.".format(input_img))
        else:
            click.echo("process: {} failed.".format(input_img))


if __name__ == '__main__':
    main()
