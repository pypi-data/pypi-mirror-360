# -*- coding: utf-8 -*-

import os

try:
    _here = os.path.dirname(__file__)
    if _here not in os.environ['PATH']:
        os.environ['PATH'] = os.path.join(_here) + ';' + os.environ['PATH']
    if 'PROJ_LIB' not in os.environ:
        os.environ['PROJ_LIB'] = os.path.join(_here)

    os.add_dll_directory(_here)
    
except Exception:
    pass






