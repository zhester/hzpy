#!/usr/bin/env PATH="$PATH" python

"""
This example shows how to prepend to $PATH in the case where the host has some
insane version of Python installed (*cough*CentOS*cough*).
"""

import sys

print( 'Running: %s' % sys.executable )
print( 'Version: %d.%d.%d' % sys.version_info )

