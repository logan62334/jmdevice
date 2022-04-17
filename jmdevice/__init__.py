# -*- coding: utf-8 -*-
import os
import sys

__version__ = '0.0.1'


def app_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)
