#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
common module
"""

import os
import sys
import logging
import ast


from .compat import basestring

logger = logging.getLogger(__name__)


def humanize_bytes(n, precision=1):
    """
    Return a humanized string representation of a number of bytes.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)

    >>> humanize_bytes(1)
    '1 B'
    >>> humanize_bytes(1024)
    '1.0 KiB'
    >>> humanize_bytes(1024 * 123)
    '123.0 KiB'
    >>> humanize_bytes(1024 * 12342)
    '12.1 MiB'
    >>> humanize_bytes(1024 * 12342, 2)
    '12.05 MiB'
    >>> humanize_bytes(1024 * 1234, 2)
    '1.21 MiB'
    >>> humanize_bytes(1024 * 1234 * 1111, 2)
    '1.31 GiB'
    >>> humanize_bytes(1024 * 1234 * 1111 * 1024)
    '1.3 TiB'
    """
    abbrevs = [
        (1 << 80, 'YiB'),
        (1 << 70, 'ZiB'),
        (1 << 60, 'EiB'),
        (1 << 50, 'PiB'),
        (1 << 40, 'TiB'),
        (1 << 30, 'GiB'),
        (1 << 20, 'MiB'),
        (1 << 10, 'KiB'),
        (1, 'B')
    ]

    if n == 1:
        return '1 B'

    for factor, suffix in abbrevs:
        if n >= factor:
            break

    return '%.*f %s' % (precision, n / factor, suffix)


def beep(a, b):
    """make a sound 
    ref: http://stackoverflow.com/questions/16573051/python-sound-alarm-when-code-finishes
    you need install  ``apt-get install sox``

    :param a: frenquency
    :param b: duration

    create a background thread,so this function does not block the main program
    """
    if sys.platform == "win32":
        import winsound

        def _beep(a, b):
            winsound.Beep(a, b * 1000)
    elif sys.platform == 'linux':
        def _beep(a, b):
            os.system(
                'play --no-show-progress --null \
                --channels 1 synth {0} sine {1}'.format(b, float(a)))
    from threading import Thread
    thread = Thread(target=_beep, args=(a, b))
    thread.daemon = True
    thread.start()


def str2pyobj(val):
    """
    basestring to python obj or not changed
    :param val:
    :return:
    """

    try:
        val = ast.literal_eval(val)
    except Exception:
        pass
    return val


def str2num(val):
    """
    str to int or float or raise a Exception. in some case maybe you just want
    to do some number type transform.
    """
    assert isinstance(val, basestring)
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except Exception as e:
            raise e


