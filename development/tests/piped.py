#!/usr/bin/env python

import sys

if ( sys.__stdin__.isatty() == False ) or ( len( sys.argv ) > 1 ):
    import fileinput
    for line in fileinput.input():
        sys.stdout.write( ' >> ' + line )

else:
    print 'enter "exit" to exit'
    while True:
        line = raw_input( '% ' )
        if line == 'exit':
            break
        print line
