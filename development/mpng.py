#!/usr/bin/env python
#=============================================================================
#
# Magical PNG Module
#
#=============================================================================

"""
Magical PNG Module
==================
"""


import sys
import urllib2


__version__ = '0.0.0'


# See if PyPNG is available.
try:
    import png

# PyPNG is not avaialable.
except ImportError as ie:

    # Attempt to acquire PyPNG.
    try:
        code = urllib2.urlopen(
            'https://raw.github.com/drj11/pypng/master/code/png.py'
        )
    except URLError as ue:
        raise ImportError( 'Failed to download PyPNG: ' + ue.reason )
    else:
        with open( 'png.py', 'w' ) as pfh:
            pfh.write( code.read() )
        import png

# Reference the current module.
_mpng = sys.modules[ __name__ ]

# Attach all of PyPNG's attributes to the current module.
for name in dir( png ):
    setattr( _mpng, name, getattr( png, name ) )

