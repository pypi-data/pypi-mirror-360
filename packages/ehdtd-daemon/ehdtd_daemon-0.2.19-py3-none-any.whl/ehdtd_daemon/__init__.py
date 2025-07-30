"""
Ehdtd daemon - Daemon script for ehdtd package

Author: Ricardo Marcelo Alvarez
Date: 2024-03-14
"""

from os.path import dirname, basename, isfile, join
import glob
import sys
import importlib.metadata

ehdtd_daemon_metadata = importlib.metadata.metadata('ehdtd_daemon')

__title__ = ehdtd_daemon_metadata['Name']
__summary__ = ehdtd_daemon_metadata['Summary']
__uri__ = ehdtd_daemon_metadata['Home-page']
__version__ = ehdtd_daemon_metadata['Version']
__author__ = ehdtd_daemon_metadata['Author']
__email__ = ehdtd_daemon_metadata['Author-email']
__license__ = ehdtd_daemon_metadata['License']
__copyright__ = 'Copyright © 2024 Ricardo Marcelo Alvarez'

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = []

if isinstance(sys.path,list):
    sys.path.append(dirname(__file__))

for f in modules:
    if isfile(f) and not f.endswith('__init__.py'):
        __all__.append(basename(f)[:-3])
