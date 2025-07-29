#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
for the sake of some compat problem
"""
import sys

version_major = sys.version_info.major
version_minor = sys.version_info.minor
######
is_py3 = ispy3 = version_major == 3
is_py2 = ispy2 = version_major == 2
######
is_py30 = ispy30 = (is_py3 and version_minor == 0)
is_py31 = ispy31 = (is_py3 and version_minor == 1)
is_py32 = ispy32 = (is_py3 and version_minor == 2)
is_py33 = ispy33 = (is_py3 and version_minor == 3)
is_py34 = ispy34 = (is_py3 and version_minor == 4)
is_py35 = ispy35 = (is_py3 and version_minor == 5)
is_py36 = ispy36 = (is_py3 and version_minor == 6)
is_py37 = ispy37 = (is_py3 and version_minor == 7)
is_py38 = ispy38 = (is_py3 and version_minor == 8)
#######
is_py24 = ispy24 = (is_py2 and version_minor == 4)
is_py25 = ispy25 = (is_py2 and version_minor == 5)
is_py26 = ispy26 = (is_py2 and version_minor == 6)
is_py27 = ispy27 = (is_py2 and version_minor == 7)

# ---------
# Platforms
# ---------
is_windows = 'win32' == sys.platform.lower()
is_linux = 'linux' == sys.platform.lower()
is_msys = 'msys' == sys.platform.lower()

builtin_str = str
str = str
bytes = bytes
basestring = (str, bytes)
numeric_types = (int, float)

# if __name__ == '__main__':
