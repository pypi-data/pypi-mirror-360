#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

from PIL import Image
import click

from pywander.path import mkdirs

logger = logging.getLogger(__name__)


def resize_image(input_img, width=0, height=0, outputdir='', outputname=''):
    """
    调整图片尺寸，保持图片的长宽比。

    宽度高度只需要指定一个即可，另外一个会自动计算得到。

    如果指定宽度或高度超过了原始尺寸，那么将不会进行操作。
    """
    img_name, img_ext = os.path.splitext(os.path.basename(input_img))

    if not os.path.exists(os.path.abspath(outputdir)):
        mkdirs(outputdir)

    if not outputname:
        outputname = img_name + '_resized' + img_ext
    else:
        output_img_name, ext = os.path.splitext(outputname)
        if not ext:
            outputname = output_img_name + '_resized' + img_ext
        elif ext != img_ext:
            raise Exception(
                'outputname ext is not the same as the intput image')

    try:
        im = Image.open(os.path.abspath(input_img))
        ori_w, ori_h = im.size

        if width == 0 and height != 0:
            width = ori_w
        elif width != 0 and height == 0:
            height = ori_h
        elif width == 0 and height == 0:
            click.echo('you must give one value , height or width', err=True)
            raise IOError

        if width > ori_w:
            logger.warning('the target width is larger than origin, '
                           'i will use the origin one')
            width = ori_w
        elif height > ori_h:
            logger.warning('the target height is larger than origin, '
                           'i will use the origin one')
            height = ori_h

        logger.debug(f'pillow resize target ({width},{height})')
        im.thumbnail((width, height))

        logger.info(os.path.abspath(input_img))

        output_img = os.path.join(os.path.abspath(outputdir), outputname)

        logger.debug(f'pillow resize output image to {output_img}')
        im.save(output_img)
        click.echo('{0} saved.'.format(output_img))
        return output_img
    except IOError:
        logging.error('IOError, I can not resize {}'.format(input_img))

    return None

