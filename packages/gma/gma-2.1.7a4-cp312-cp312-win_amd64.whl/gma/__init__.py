# -*- coding: utf-8 -*-

from . import climet, gft, io, crs, rsvi, math, osf, smc, rasp, vesp
from .algos.core import env

try:
    from importlib.metadata import version
    __version__ = version(__name__)
except: 
    __version__ = "unknown"
finally:
    del version
    
try:
    from . import algos
    __gdalversion__ = algos.dataio.base._gdal.VersionInfo("RELEASE_NAME")
except:
    __gdalversion__ = "0.0.0"
      
if __gdalversion__ < '3.10.0':
    raise ImportError(f'The GDAL version is too low, the current version {__gdalversion__}, '
                      'the minimum version is 3.4.1, please update GDAL!')



