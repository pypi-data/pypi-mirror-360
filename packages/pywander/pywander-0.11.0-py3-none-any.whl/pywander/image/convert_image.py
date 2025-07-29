#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging
import os.path
import subprocess
import shutil

from PIL import Image

from pywander.unique_key import random_md5
from pywander.path import mkdirs
from pywander.exceptions import PdftocairoProcessError, PillowProcessError, InkscapeProcessError
from pywander.utils.command_utils import get_command_path
from .utils import detect_output_file_exist

logger = logging.getLogger(__name__)

pillow_support = ['png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp', 'ppm']


def convert_image_by_pillow(input_img, outputdir, output_img_name, outputformat='png', overwrite=True):
    """

    """
    output_img = detect_output_file_exist(outputdir, output_img_name, outputformat, overwrite)
    if not output_img:
        return None

    if input_img == output_img:
        raise FileExistsError

    try:
        img = Image.open(input_img)
        img.save(output_img)
        logger.info('{0} saved.'.format(output_img))
        return output_img
    except FileNotFoundError as e:
        raise PillowProcessError(
            f"process image: {input_img} raise FileNotFoundError")
    except IOError:
        raise PillowProcessError(f"process image: {input_img} raise IOError")


def convert_image_by_inkscape(input_img, outputdir, output_img_name, outputformat='png', overwrite=True, dpi=150):
    output_img = detect_output_file_exist(outputdir, output_img_name, outputformat, overwrite)
    if not output_img:
        return None

    if input_img == output_img:
        raise FileExistsError

    inkscape_command = get_command_path('inkscape')

    process_cmd = [inkscape_command, f'--export-type={outputformat}', '-d', str(dpi), input_img]
    logger.debug(f'start call cmd {process_cmd}')
    subprocess.check_call(process_cmd)
    return output_img


def convert_image_by_pdftocairo(input_img, outputdir, output_img_name, outputname='', outputformat='png',
                                overwrite=True, dpi=150, transparent=False):
    """
    pdftocairo对中文名文件支持不太好，先输出到临时文件，再更改名字

    """
    output_img = detect_output_file_exist(outputdir, output_img_name, outputformat, overwrite)
    if not output_img:
        return None

    if not shutil.which('pdftocairo'):
        raise PdftocairoProcessError("pdftocairo command not found.")

    cur_dir = os.path.abspath(os.curdir)
    os.chdir(outputdir)

    map_dict = {i: '-{}'.format(i) for i in
                ['png', 'pdf', 'ps', 'eps', 'jpeg', 'svg']}

    out_flag = map_dict[outputformat]

    temp_out_name = 'temp_' + random_md5(limit=10)
    temp_out_filename = f'{temp_out_name}.{outputformat}'

    if outputformat in ['png', 'jpeg']:
        # png jpeg without ext so use the output_img_name
        process_cmd = ['pdftocairo', out_flag, '-singlefile', '-r', str(dpi),
                       input_img, temp_out_name]

        if transparent and outputformat == 'png':
            process_cmd.insert(2, '-transp')

        logger.debug(f'start call cmd {process_cmd}')
        subprocess.check_call(process_cmd)

    else:
        process_cmd = ['pdftocairo', out_flag, '-r', str(dpi), input_img,
                       temp_out_filename]
        if transparent and outputformat == 'tiff':
            process_cmd.insert(2, '-transp')

        logger.debug(f'start call cmd {process_cmd}')
        subprocess.check_call(process_cmd)

    if overwrite:
        os.replace(temp_out_filename, output_img)
    else:
        os.rename(temp_out_filename, output_img)

    os.chdir(cur_dir)
    return output_img


def convert_image(input_img, outputformat='png', dpi=150, outputdir='',
                  outputname='', overwrite=True, transparent=False):
    """
    - intput_img 输入图片
    - outputformat
    - dpi 输出图片dpi
    - overwrite 图片是否覆写
    - outputname 输出图片名 带后缀
    - output_img_name 输出图片名 不带后缀

    本函数若图片转换成功则返回目标在系统中的路径，否则返回None。
    文件basedir路径默认和input_img相同
    """
    input_img = os.path.abspath(input_img)

    outputdir = os.path.abspath(outputdir)
    if not os.path.exists(outputdir):
        mkdirs(outputdir)

    img_name, img_ext = os.path.splitext(os.path.basename(input_img))

    if not outputname:
        outputname = img_name + '.{}'.format(outputformat)
        output_img_name = img_name
    else:
        output_img_name, ext = os.path.splitext(outputname)
        if not ext:
            outputname = output_img_name + '.{}'.format(outputformat)
        elif ext != outputformat:
            raise Exception(
                'outputname ext is not the same as the outputformat')

    try:
        if img_ext[1:] in pillow_support and outputformat in pillow_support:
            return convert_image_by_pillow(input_img, outputdir, output_img_name, outputformat=outputformat,
                                           overwrite=overwrite)

        elif img_ext[1:] in ['svg', 'svgz'] and outputformat in ['png', 'pdf', 'ps', 'eps']:
            return convert_image_by_inkscape(input_img, outputdir, output_img_name, outputformat=outputformat,
                                             dpi=dpi, overwrite=overwrite)

        elif img_ext[1:] in ['pdf'] and outputformat in ['png', 'jpeg', 'ps', 'eps', 'svg']:
            return convert_image_by_pdftocairo(input_img, outputdir, output_img_name, outputname=outputname,
                                               outputformat=outputformat, dpi=dpi, overwrite=overwrite,
                                               transparent=transparent)
    except PillowProcessError as e:
        logger.error(e)
    except InkscapeProcessError as e:
        logger.error(e)
    except PdftocairoProcessError as e:
        logger.error(e)

    return None
